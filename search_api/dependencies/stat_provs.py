import csv
import os
import uuid
from contextlib import contextmanager

import psycopg2
from flask import current_app, g
from search_api.exceptions import ApplicationError
from search_api.extensions import db


@contextmanager
def getcursor():  # pragma: no cover
    con = db.engine.raw_connection()
    try:
        yield con.cursor()
    finally:
        con.commit()  # Not sure why this is required
        con.close()


def update_stat_provs_data():
    cwd = os.getcwd()
    with getcursor() as cur:
        try:
            # Read in the statutory provisions csv file
            source_dir = os.path.join(cwd, 'search_api/static')
            g.trace_id = uuid.uuid4().hex

            # process the add stat provs csv
            with open(os.path.join(source_dir, 'add_stat_provs.csv'), 'r', encoding='utf8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                current_app.logger.info(csv_reader)

                for stat_prov in csv_reader:
                    new_stat_prov = stat_prov[0]
                    # check to see if the stat prov already exists in the database
                    print("Checking if {} stat prov already exists".format(new_stat_prov))
                    cur.execute("SELECT * FROM statutory_provision WHERE title = %s", (new_stat_prov,))
                    count = cur.rowcount
                    if count > 0:
                        print("Ignoring add {} as it is an existing stat prov".format(new_stat_prov))
                    else:
                        #  Create a new Stat_Prov entry using amended_stat_prov as the title/display_title
                        cur.execute("""INSERT INTO statutory_provision (title, selectable, display_title)
                                                                            VALUES (%s, %s, %s)""",
                                    (new_stat_prov, 'True', new_stat_prov))
                        print("New statutory provision added {}".format(new_stat_prov))

            # process the amend stat provs csv
            with open(os.path.join(source_dir, 'amend_stat_provs.csv'), 'r', encoding='utf8') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                current_app.logger.info(csv_reader)
                line_count = 0

                for stat_prov in csv_reader:

                    existing_stat_prov = stat_prov[0]
                    amended_stat_prov = stat_prov[1]

                    if line_count == 0:
                        # Ignore the header line during the import
                        pass
                    else:
                        # check to see if the stat prov exists in the database
                        print("Checking for {} existing stat prov".format(existing_stat_prov))
                        cur.execute("SELECT * FROM statutory_provision WHERE title = %s", (existing_stat_prov,))
                        count = cur.rowcount
                        if count == 0:
                            print("Ignoring {} doesn't exist as existing stat prov".format(existing_stat_prov))
                        else:
                            # Update all existing stat provs that have a display_title matching the existing title
                            cur.execute("""UPDATE statutory_provision
                                SET selectable = %s, display_title = %s
                                WHERE display_title = %s""", ('False', amended_stat_prov, existing_stat_prov))
                            if cur.rowcount == 0:
                                print("No records found matching {}".format(existing_stat_prov))
                            else:
                                print("Update {} to {}".format(existing_stat_prov, amended_stat_prov))

                            # Check to see if a Stat_prov already exists in the db
                            cur.execute("SELECT * FROM statutory_provision WHERE title = %s", (amended_stat_prov,))
                            count = cur.rowcount
                            if count == 0:
                                #  Create a new Stat_Prov entry using amended_stat_prov as the title/display_title
                                cur.execute("""INSERT INTO statutory_provision (title, selectable, display_title)
                                        VALUES (%s, %s, %s)""", (amended_stat_prov, 'True', amended_stat_prov))
                                print("Added {}, {}".format(amended_stat_prov, amended_stat_prov))
                            else:
                                # If the record is already in the DB, then update it
                                cur.execute("""UPDATE statutory_provision SET selectable = %s
                                            WHERE title = %s""", ('True', amended_stat_prov))
                                print("Update selectable value for {}".format(amended_stat_prov))

                    line_count += 1

        # Run an update query to update the charge_category_stat_provisions link table after amending stat provs.
        # This means that the CSV can now be used to update Express Stat Provs.
            cur.execute("""UPDATE charge_categories_stat_provisions a SET statutory_provision_id = (SELECT c.id
                     FROM statutory_provision b, statutory_provision c WHERE b.display_title = c.title
                     and b.id = a.statutory_provision_id) WHERE statutory_provision_id in
                     (SELECT statutory_provision_id FROM charge_categories_stat_provisions d, statutory_provision e
                     WHERE d.statutory_provision_id = e.id AND e.selectable is False)""")

        except (IOError, OSError) as e:
            current_app.logger.exception(str(e))
            return "Error opening " + source_dir

        except psycopg2.Error as e:
            current_app.logger.exception('Application Error: %s', repr(e))
            raise ApplicationError("Statutory Provisions update Error", "E999")
