"""add and modify stat provs

Revision ID: f14dd341e520
Revises: 45eaaa5da9e0
Create Date: 2019-11-25 15:30:24.171726

"""

# revision identifiers, used by Alembic.
revision = 'f14dd341e520'
down_revision = '45eaaa5da9e0'

from alembic import op
from sqlalchemy.sql import text

add_stat_provs = ["Wildlife and Countryside Act 1981 section 28C(6)",
                  "Water Industry Act 1991 Part 3 section 82(5)",
                  "Anglian Water Authority Act 1977 section 30",
                  "Local Government (Miscellaneous Provisions) Act 1982 section 29"]

amend_stat_provs = [["Housing Act 1985 part IX sub-section 265", "Housing Act 1985 part IX section 265"],
["Housing Act 1985 part IX sub-section 294", "Housing Act 1985 part IX section 294"],
["Housing Act 1985 sub-section 264", "Housing Act 1985 section 264"],
["Housing Act 2004 sub-section 11", "Housing Act 2004 section 11"],
["Housing Act 2004 sub-section 12", "Housing Act 2004 section 12"],
["Housing Act 2004 sub-section 20", "Housing Act 2004 section 20"],
["Housing Act 2004 sub-section 21", "Housing Act 2004 section 21"],
["Local Government and Housing Act 1989 sub-section 119", "Local Government and Housing Act 1989 section 119"],
["Local Government and Housing Act 1989 sub-section 121", "Local Government and Housing Act 1989 section 121"],
["Local Government and Housing Act 1989 sub-section 122", "Local Government and Housing Act 1989 section 122"],
["Local Government and Housing Act 1989 sub-section 123", "Local Government and Housing Act 1989 section 123"],
["Opencast Coal Act 1958 sub-section 11(1)", "Opencast Coal Act 1958 section 11(1)"],
["Opencast Coal Act 1958 sub-section 16(6)", "Opencast Coal Act 1958 section 16(6)"],
["Public Health Act 1875 sub-section 23", "Public Health Act 1875 section 23"],
["Public Health Act 1875 sub-section 24", "Public Health Act 1875 section 24"],
["Public Health Act 1875 sub-section 26", "Public Health Act 1875 section 26"],
["Town and Country Planning Act 1954 sub-section 28", "Town and Country Planning Act 1954 section 28"],
["Town and Country Planning Act 1954 sub-section 57", "Town and Country Planning Act 1954 section 57"],
["Town and Country Planning Act 1971 sub-section 158", "Town and Country Planning Act 1971 section 158"],
["Town and Country Planning Act 1971 sub-section 159", "Town and Country Planning Act 1971 section 159"],
["Conservation of Habitats and Species regulations 2010, regulation 13", "Conservation of Habitats and Species regulations 2010 regulation 13"],
["Crossrail Act 2008, section 47(10)", "Crossrail Act 2008 section 47(10)"],
["Environmental Permitting (England and Wales) Regulations 2010, regulation 15", "Environmental Permitting (England and Wales) regulations 2010 regulation 15"],
["Flood and Water Management Act 2010, schedule 1 (Effect of Designation), paragraph 5(1)", "Flood and Water Management Act 2010 schedule 1 paragraph 5(1)"],
["Housing Act 2004 schedule 7, section 132, paragraph 10(9)", "Housing Act 2004 schedule 7 section 132 paragraph 10(9)"],
["Housing Act 2004 schedule 7, section 132, paragraph 2", "Housing Act 2004 schedule 7 section 132 paragraph 2"],
["Leasehold Reform, Housing and Urban Development Act 1993 section 70", "Leasehold Reform Housing and Urban Development Act 1993 section 70"],
["Thames Water Utilities Limited (Thames Tidway Tunnel) Order 2014, section 52(8)", "Thames Water Utilities Limited (Thames Tideway Tunnel) Order 2014 section 52(8)"],
["Town and Country Planning (Control of Advertisements) (England) regulations 1960, regulations 23", "Town and Country Planning (Control of Advertisements) (England) regulations 1960 regulation 23"],
["Community Infrastructure Levy Regulations 2010 regulation 66(1)", "Community Infrastructure Levy regulations 2010 regulation 66(1)"],
["Caravan Sites and Control of Development Act 1960 section 9(3)", "Caravan Sites and Control of Development Act 1960 section 9I(3)"],
["Wildlife and Countryside Act 1981 section 28", "Wildlife and Countryside Act 1981 section 28(9)"],
["Local Land Charges Act 1977 section 6(2)", "Local Land Charges Act 1975 section 6(2)"],
["London Building Acts (Amendment) At 1939 section 70(2)(a)", "London Building Acts (Amendment) Act 1939 section 70(2)(a)"]]


def upgrade():
    conn = op.get_bind()

    for stat_prov in add_stat_provs:
        # Add new stat provs
        stat_prov_id = get_stat_prov_id(stat_prov, conn)
        if not stat_prov_id:
            query = "INSERT INTO statutory_provision " \
                    "(title, selectable, display_title) VALUES ('{0}', '{1}', '{0}');"\
                .format(stat_prov, 'True')
            op.execute(query)

    for stat_provs in amend_stat_provs:
        old_stat_prov = stat_provs[0]
        new_stat_prov = stat_provs[1]
        old_stat_prov_id = get_stat_prov_id(old_stat_prov, conn)
        new_stat_prov_id = get_stat_prov_id(new_stat_prov, conn)

        # Update all existing stat provs that have a display_title matching the existing title
        if old_stat_prov_id:
            query = "UPDATE statutory_provision " \
                    "SET selectable = '{2}', display_title = '{1}' " \
                    "WHERE id = '{0}';" \
                .format(old_stat_prov_id, new_stat_prov, 'False')
            op.execute(query)

        # If the record is already in the DB, then update it
        if new_stat_prov_id:
            query = "UPDATE statutory_provision " \
                    "SET selectable = '{1}' " \
                    "WHERE id = '{0}';" \
                .format(new_stat_prov_id, 'True')
            op.execute(query)
        else:
            # Create a new Stat_Prov entry using new_stat_prov as the title/display_title
            query = "INSERT INTO statutory_provision " \
                    "(title, selectable, display_title) VALUES ('{0}', '{1}', '{0}') RETURNING id;" \
                .format(new_stat_prov, 'True')
            res = conn.execute(text(query))
            results = res.fetchall()
            new_stat_prov_id = results[0][0]

        # Update charge cat stat provs with new stat prov ID
        if old_stat_prov_id and new_stat_prov_id:
            query = "UPDATE charge_categories_stat_provisions " \
                    "SET statutory_provision_id = {0} " \
                    "WHERE statutory_provision_id = {1}"\
                .format(new_stat_prov_id, old_stat_prov_id)
            op.execute(query)


def downgrade():
    conn = op.get_bind()

    for stat_prov in add_stat_provs:
        # Remove new stat provs
        stat_prov_id = get_stat_prov_id(stat_prov, conn)
        if stat_prov_id:
            query = "DELETE FROM statutory_provision " \
                    "WHERE id = '{0}';"\
                .format(stat_prov_id)
            op.execute(query)

    for stat_provs in amend_stat_provs:
        old_stat_prov = stat_provs[0]
        new_stat_prov = stat_provs[1]

        # Update charge cat stat provs with old stat prov ID
        old_stat_prov_id = get_stat_prov_id(old_stat_prov, conn)
        new_stat_prov_id = get_stat_prov_id(new_stat_prov, conn)
        if old_stat_prov_id and new_stat_prov_id:
            query = "UPDATE charge_categories_stat_provisions " \
                    "SET statutory_provision_id = {0} " \
                    "WHERE statutory_provision_id = {1};"\
                .format(old_stat_prov_id, new_stat_prov_id)
            op.execute(query)

        # Remove Stat_Prov entries for new_stat_prov
        if new_stat_prov_id:
            query = "DELETE FROM statutory_provision " \
                    "WHERE id = '{0}';" \
                .format(new_stat_prov_id)
            op.execute(query)

        # Update all old stat provs to reset their display title to the old title and set selectable to true
        if old_stat_prov_id:
            query = "UPDATE statutory_provision " \
                    "SET selectable = '{2}', display_title = '{1}' " \
                    "WHERE id = '{0}';" \
                .format(old_stat_prov_id, old_stat_prov, 'True')
            op.execute(query)


def get_stat_prov_id(stat_prov, conn):
    query = "SELECT id FROM statutory_provision WHERE title = '{}';".format(stat_prov)
    res = conn.execute(text(query))
    results = res.fetchall()
    if results is None or len(results) == 0:
        # Need to return None rather than except, because if the old csv script was run then db might be in a
        # different state to what we expect
        return None
    return results[0][0]
