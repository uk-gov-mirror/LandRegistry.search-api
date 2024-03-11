"""Add 28 new and delete 1 unrequired, Statutory Provisions.

Revision ID: f5bece98f1a1
Revises: 2ede2fa7ea8a
Create Date: 2018-10-04 11:17:58.840747

"""

# revision identifiers, used by Alembic.
revision = 'f5bece98f1a1'
down_revision = '2ede2fa7ea8a'

import sqlalchemy as sa
from alembic import op

provision_list = ["Children and Young Persons Act 1993 section 12C(5)",
                    "City of London (Various Powers) Act 1960 section 33",
                    "City of London (Various Powers) Act 1967 section 6",
                    "Civil Aviation Act 1982 section 55",
                    "Conservation (Natural Habitats, &c) Regulations 1994 regulation 22 paragraph 4",
                    "Conservation of Habitats and Species Regulations 2010 regulation 35(4)", 
                    "Conservation of Habitats and Species Regulations 2010, regulation 25 paragraph 4",
                    "Conservation of Habitats and Species Regulations 2017 regulation 17(4)",
                    "Conservation of Habitats and Species Regulations 2017 regulation 27(4)", 
                    "Countryside and Rights of Way Act 2000 schedule 9 paragraph 28(9)",
                    "Criminal Justice and Immigration Act 2008 section 143", 
                    "Gas Act 1965 section 11(3)",
                    "Greater London Council (General Powers) Act 1973 section 24",
                    "Greater London Council (General Powers) Act 1974 section 16",
                    "Greater London Council (General Powers) Act 1986",
                    "Harbours Act 1964 schedule 3 paragraph 24(2F)",
                    "High Speed Rail (London—West Midlands) Act 2017 section 51",
                    "High Speed Rail (London—West Midlands) Act 2017 schedule 14",
                    "Housing Act 1985 section 37", 
                    "Housing Act 1985 section 239", 
                    "Housing Act 2004 section 37", 
                    "Housing Act 2004 section 74", 
                    "Housing Act 2004 Schedule 7 paragraph 23(9)",
                    "London County Council (General Powers) Act 1962 section 23(10)",
                    "Mission and Pastoral Measure 2011 section 78", 
                    "Pipe-lines Act 1962 schedule 2 paragraph 7(6)",
                    "Thames Barrier and Flood Prevention Act 1972 section 68(6)", 
                    "Compulsory Purchase(Vesting Declarations) Act 1981 section 3A(4)",
                    "Space Industry Act 2018 section 45",
                    "Ecclesiastical Jurisdiction and Care of Churches Measure 2018 No. 3 section 92",
                    "Town and Country Planning Act 1990 section 207"
                    ]

def upgrade():
    for provision in provision_list:
        selectable = "TRUE"
        query = "INSERT INTO statutory_provision (title, selectable) VALUES ('{0}', {1});"\
            .format(provision, selectable)
        op.execute(query)
    query = "UPDATE statutory_provision set selectable = FALSE where title = 'Local Land Charges Act 1977 section 6(2)'"
    op.execute(query)


def downgrade():
    for provision in provision_list:
        query = "DELETE from statutory_provision WHERE title = '{0}';".format(provision)
        op.execute(query)
    query = "UPDATE statutory_provision set selectable = TRUE where title = 'Local Land Charges Act 1977 section 6(2)'"
    op.execute(query)
