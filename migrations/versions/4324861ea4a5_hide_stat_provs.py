"""hide stat provs

Revision ID: 4324861ea4a5
Revises: 0dfa2bf78ef3
Create Date: 2020-06-08 07:31:21.870042

"""

# revision identifiers, used by Alembic.
revision = '4324861ea4a5'
down_revision = '0dfa2bf78ef3'

import sqlalchemy as sa
from alembic import op

stat_prov_list = [
    'Ancient Monuments Act 1931',
    'Leasehold Reform Act 1967',
    'Agriculture Act 1947',
    'Part XI of the Highways Act 1980',
    'New Streets Act 1951',
    'Private Street Works Act 1892',
    'Housing Act 1974',
    'Education (Inner London Education Authority) (Property Transfer) Order 1990',
    'Housing Act 1985',
    'Planning (Consequential Provisions) Act 1990 schedule 3',
    'Land Compensation Act 1973',
    'Town and Country Planning (Control of Advertisements) regulations 1989 SI 1989/670',
    'Greater London Council (General Powers) Act 1986',
    'Environment Act 1995',
    'Field Monuments Act 1972',
    'Housing Act 1964',
    'Town and Country Planning (Control of Advertisements) (England) regulations 2007 SI 2007/783',
    'Pastoral Measure 1968',
    'Housing Associations Act 1985',
    'Public Utilities and Street Works Act 1950',
    'Control of Pollution Act 1974',
    'Town and Country Planning (Control of Advertisements) regulations 1987 SI 1987/804',
    'Town and Country Planning Act 1990',
    'National Parks and Access to the Countryside Act 1949 part III',
    'New Streets Act 1957',
    'Town and Country Planning (Control of Advertisements) (Amendment Number 2) regulations 1987 SI 1987/2227',
    'Town and Country Planning Act 1971',
    'Civil Aviation Act 1949',
    'Regulatory Reform (Housing Assistance) (England and Wales) Order 2002',
    'Town and Country Planning Act 1990 schedule 9',
    'House Purchase and Housing Act 1959',
    'New Towns Act 1946',
    'Development of Rural Wales Act 1976',
    'Housing Act 1985 schedule 18',
    'Housing (Financial Provisions) Act 1958',
    'General Rate Act 1967',
    'Small Dwellings Acquisition Act 1899',
    'Town and Country Planning (Control of Advertisements) regulations 1992 SI 1992/666',
    'New Towns Act 1965',
    'Agriculture Act 1967 schedule 3',
    'Town and Country Planning Act 1968',
    'Clean Air Act 1956',
    'Housing Act 1980',
    'Historic Buildings and Ancient Monuments Act 1953',
    'Public Health Act 1936',
    'Covent Garden Market Act 1966',
    'Highways Act 1971',
    'Code of 1875',
    'Education (London Residuary Body) (Property Transfer) Order 1991',
    'Highways Act 1959',
    'Town and Country Planning (Control of Advertisements) (England) regulations 2007',
    'European Communities Act 1972',
    'Public Health Act 1961',
    'Cardiff Bay Barrage Act 1993',
    'Town and Country Planning (Control of Advertisements) regulations 1984 SI 1984/421',
    'Wentworth Estate Act 1964',
    'Housing Act 1961',
    'Housing Act 1957',
    'Clean Air Act 1968'
]


def upgrade():
    for stat_prov in stat_prov_list:
        query = "UPDATE statutory_provision set selectable = FALSE where title = '{}'".format(stat_prov)
        op.execute(query)



def downgrade():
    for stat_prov in stat_prov_list:
        query = "UPDATE statutory_provision set selectable = TRUE where title = '{}'".format(stat_prov)
        op.execute(query)
