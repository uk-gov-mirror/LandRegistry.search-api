"""Load category and statutory provisions data.

Revision ID: 3de2b88f738b
Revises: dec5daa38b6c
Create Date: 2018-03-14 17:37:06.475228

"""

# revision identifiers, used by Alembic.
revision = '3de2b88f738b'
down_revision = 'dec5daa38b6c'

from alembic import op
from sqlalchemy.sql import text

statutory_provisions = {
    "Acquisition of Land Act 1981 section 15(6)": 't',
    "Acquisition of Land Act 1981 schedule 1 paragraph 6": 't',
    "Agriculture (Miscellaneous Provisions) Act 1941 section 8(4)": 't',
    "Agriculture Act 1947": 't',
    "Agriculture Act 1967 schedule 3": 't',
    "Agriculture Act 1967 section 45(6)": 't',
    "Agriculture Act 1986 section 18(7)": 't',
    "Ancient Monuments Act 1931": 't',
    "Ancient Monuments and Archaeological Areas Act 1979 section 1(9)": 't',
    "Ancient Monuments and Archaeological Areas Act 1979 section 12": 't',
    "Ancient Monuments and Archaeological Areas Act 1979 section 16(8)": 't',
    "Ancient Monuments and Archaeological Areas Act 1979 section 2(3)": 't',
    "Ancient Monuments and Archaeological Areas Act 1979 section 33(5)": 't',
    "Ancient Monuments and Archaeological Areas Act 1979 section 8(6)": 't',
    "Ancient Monuments and Archaeological Areas Act 1979 section 12(7)": 't',
    "Anti-Social Behaviour Act 2003 section 69": 't',
    "Anti-Social Behaviour Act 2003 section 77(3)": 't',
    "Building Act 1984 section 107": 't',
    "Building Act 1984 section 18": 't',
    "Building Act 1984 section 19": 't',
    "Building Act 1984 section 22": 't',
    "Building Act 1984 section 23(2)": 't',
    "Building Act 1984 section 36": 't',
    "Building Act 1984 section 59": 't',
    "Building Act 1984 section 64": 't',
    "Building Act 1984 section 65": 't',
    "Building Act 1984 section 66": 't',
    "Building Act 1984 section 69": 't',
    "Building Act 1984 section 70": 't',
    "Building Act 1984 section 71": 't',
    "Building Act 1984 section 72": 't',
    "Building Act 1984 section 74": 't',
    "Building Act 1984 section 75": 't',
    "Building Act 1984 section 76": 't',
    "Building Act 1984 section 77": 't',
    "Building Act 1984 section 78": 't',
    "Building Act 1984 section 79": 't',
    "Building Act 1984 section 82": 't',
    "Building Act 1984 section 84": 't',
    "Caravan Sites and Control of Development Act 1960 section 9(3)": 't',
    "Cardiff Bay Barrage Act 1993": 't',
    "Care of Churches and Ecclesiastical Jurisdiction Measure 1991 (No. 1) section 22(8)": 't',
    "Civil Aviation Act 1949": 't',
    "Civil Aviation Act 1968 section 21": 't',
    "Civil Aviation Act 1971 section 16(2)": 't',
    "Civil Aviation Act 1982 section 43": 't',
    "Civil Aviation Act 1982 section 44": 't',
    "Civil Aviation Act 1982 section 45": 't',
    "Civil Aviation Act 1982 section 46(1)": 't',
    "Clean Air Act 1956": 't',
    "Clean Air Act 1968": 't',
    "Clean Air Act 1993 section 18": 't',
    "Clean Air Act 1993 section 24": 't',
    "Coast Protection Act 1949 section 10": 't',
    "Coast Protection Act 1949 section 12": 't',
    "Coast Protection Act 1949 section 13": 't',
    "Coast Protection Act 1949 section 8": 't',
    "Code of 1875": 't',
    "Community Infrastructure Levy Regulations 2010 regulation 66(1)": 't',
    "Compulsory Purchase (Vesting Declarations) Act 1981 section 3(4)": 't',
    "Conservation (Natural Habitats) regulations 1994 regulation 11": 't',
    "Conservation (Natural Habitats) regulations 1994 regulation 14": 't',
    "Conservation of Habitats and Species regulations 2010, regulation 13": 't',
    "Control of Pollution Act 1974": 't',
    "Countryside Act 1968 section 28": 't',
    "Countryside Act 1968 section 29": 't',
    "Countryside and Rights of Way Act 2000 section 16": 't',
    "Covent Garden Market Act 1966": 't',
    "Crossrail Act 2008, section 47(10)": 't',
    "Development of Rural Wales Act 1976": 't',
    "District Councils (Water Supply Facilities) Act 1897 section 2": 't',
    "Disused Burial Grounds (Amendment) Act 1981 section 2(4)": 't',
    "Education (Inner London Education Authority) (Property Transfer) Order 1990": 't',
    "Education (London Residuary Body) (Property Transfer) Order 1991": 't',
    "Energy Act 2013 section 123(3)": 't',
    "Environment Act 1995": 't',
    "Environmental Protection Act 1990 section 80": 't',
    "Environmental Protection Act 1990 section 81A": 't',
    "Environmental Protection Act 1990 section 81B": 't',
    "European Communities Act 1972": 't',
    "Field Monuments Act 1972": 't',
    "Forestry Act 1967 Schedule 5 paragraph 2F": 't',
    "Gas Act 1965 section 5(10)": 't',
    "General Rate Act 1967": 't',
    "Greater London Council (General Powers) Act 1973 section 28(b)": 't',
    "Highways Act 1959": 't',
    "Highways Act 1959 section 189": 't',
    "Highways Act 1971": 't',
    "Highways Act 1980 section 133": 't',
    "Highways Act 1980 section 134": 't',
    "Highways Act 1980 section 146": 't',
    "Highways Act 1980 section 147": 't',
    "Highways Act 1980 section 152": 't',
    "Highways Act 1980 section 153": 't',
    "Highways Act 1980 section 154": 't',
    "Highways Act 1980 section 164(2)": 't',
    "Highways Act 1980 section 165": 't',
    "Highways Act 1980 section 166": 't',
    "Highways Act 1980 section 167": 't',
    "Highways Act 1980 section 176": 't',
    "Highways Act 1980 section 177": 't',
    "Highways Act 1980 section 178": 't',
    "Highways Act 1980 section 180": 't',
    "Highways Act 1980 section 184": 't',
    "Highways Act 1980 section 212": 't',
    "Highways Act 1980 section 224": 't',
    "Highways Act 1980 section 230": 't',
    "Highways Act 1980 section 253": 't',
    "Highways Act 1980 section 278": 't',
    "Highways Act 1980 section 305": 't',
    "Highways Act 1980 section 35": 't',
    "Highways Act 1980 section 38": 't',
    "Highways Act 1980 section 73": 't',
    "Highways Act 1980 section 74": 't',
    "Highways Act 1980 section 79": 't',
    "Highways Act 1980 section 87": 't',
    "Hill Farming Act 1954 section 2": 't',
    "Historic Buildings and Ancient Monuments Act 1953": 't',
    "House Purchase and Housing Act 1959": 't',
    "Housing (Financial Provisions) Act 1958": 't',
    "Housing (Rural Workers) Act 1926 section 3": 't',
    "Housing Act 1923 section 2": 't',
    "Housing Act 1957": 't',
    "Housing Act 1961": 't',
    "Housing Act 1964": 't',
    "Housing Act 1974": 't',
    "Housing Act 1980": 't',
    "Housing Act 1985": 't',
    "Housing Act 1985 part IX section 265": 't',
    "Housing Act 1985 part IX section 266": 't',
    "Housing Act 1985 part IX section 282": 't',
    "Housing Act 1985 part IX sub-section 265": 't',
    "Housing Act 1985 part IX sub-section 294": 't',
    "Housing Act 1985 schedule 18": 't',
    "Housing Act 1985 section 156A": 't',
    "Housing Act 1985 section 157(2)": 't',
    "Housing Act 1985 section 189": 't',
    "Housing Act 1985 section 190": 't',
    "Housing Act 1985 section 200": 't',
    "Housing Act 1985 section 210": 't',
    "Housing Act 1985 section 215": 't',
    "Housing Act 1985 section 220": 't',
    "Housing Act 1985 section 229": 't',
    "Housing Act 1985 section 264": 't',
    "Housing Act 1985 section 265": 't',
    "Housing Act 1985 section 269": 't',
    "Housing Act 1985 section 270": 't',
    "Housing Act 1985 section 272": 't',
    "Housing Act 1985 section 354": 't',
    "Housing Act 1985 section 36A": 't',
    "Housing Act 1985 section 37(1)": 't',
    "Housing Act 1985 section 370": 't',
    "Housing Act 1985 section 375": 't',
    "Housing Act 1985 section 379": 't',
    "Housing Act 1985 section 384": 't',
    "Housing Act 1985 section 609": 't',
    "Housing Act 1985 sub-section 264": 't',
    "Housing Act 1988 section 2A": 't',
    "Housing Act 1996 section 12A": 't',
    "Housing Act 1996 section 13": 't',
    "Housing Act 2004 schedule 7, section 132, paragraph 10(9)": 't',
    "Housing Act 2004 schedule 7, section 132, paragraph 2": 't',
    "Housing Act 2004 section 102 AND section 107(9)": 't',
    "Housing Act 2004 section 116(9) AND section 119": 't',
    "Housing Act 2004 section 129(7)": 't',
    "Housing Act 2004 section 129(8)": 't',
    "Housing Act 2004 section 43": 't',
    "Housing Act 2004 section 49": 't',
    "Housing Act 2004 section 50": 't',
    "Housing Act 2004 section 73": 't',
    "Housing Act 2004 sub-section 11": 't',
    "Housing Act 2004 sub-section 12": 't',
    "Housing Act 2004 sub-section 20": 't',
    "Housing Act 2004 sub-section 21": 't',
    "Housing Associations Act 1985": 't',
    "Housing Grants, Construction and Regeneration Act 1996 section 52": 't',
    "Housing Grants, Construction and Regeneration Act 1996 section 81": 't',
    "Housing Grants, Construction and Regeneration Act 1996 section 87": 't',
    "Housing Grants, Construction and Regeneration Act 1996 section 88": 't',
    "Land Compensation Act 1973": 't',
    "Land Compensation Act 1973 section 52(8)": 't',
    "Land Compensation Act 1973 section 8(4)": 't',
    "Land Drainage Act 1976 section 31(4)": 't',
    "Land Drainage Act 1991 section 18(8)": 't',
    "Land Powers (Defence) Act 1958 section 17": 't',
    "Leasehold Reform Act 1967": 't',
    "Leasehold Reform, Housing and Urban Development Act 1993 section 70": 't',
    "Local Government (Miscellaneous Provisions) Act 1976 section 35": 't',
    "Local Government (Miscellaneous Provisions) Act 1982 section 33": 't',
    "Local Government and Housing Act 1989 section 89(8)": 't',
    "Local Government and Housing Act 1989 sub-section 119": 't',
    "Local Government and Housing Act 1989 sub-section 121": 't',
    "Local Government and Housing Act 1989 sub-section 122": 't',
    "Local Government and Housing Act 1989 sub-section 123": 't',
    "Local Land Charges Act 1975 section 6(2)": 't',
    "Local Land Charges Act 1977 section 6(2)": 't',
    "Localism Act 2011 section 100(a)": 't',
    "London Building Acts (Amendment) At 1939 section 70(2)(a)": 't',
    "National Parks and Access to the Countryside Act 1949 part III": 't',
    "National Parks and Access to the Countryside Act 1949 section 21": 't',
    "National Parks and Access to the Countryside Act 1949 section 64": 't',
    "National Parks and Access to the Countryside Act 1949 section 65": 't',
    "New Roads and Street Works Act 1991 section 87": 't',
    "New Streets Act 1951": 't',
    "New Streets Act 1957": 't',
    "New Towns Act 1946": 't',
    "New Towns Act 1965": 't',
    "New Towns Act 1981 section 1(5)": 't',
    "New Towns Act 1981 section 12": 't',
    "Opencast Coal Act 1958 sub-section 11(1)": 't',
    "Opencast Coal Act 1958 sub-section 16(6)": 't',
    "Part XI of the Highways Act 1980": 't',
    "Pastoral Measure 1968": 't',
    "Pastoral Measure 1983 section 65": 't',
    "Planning (Consequential Provisions) Act 1990 schedule 3": 't',
    "Planning (Hazardous Substances) Act 1990 section 10": 't',
    "Planning (Hazardous Substances) Act 1990 section 24": 't',
    "Planning (Hazardous Substances) Act 1990 section 27": 't',
    "Planning (Listed Buildings and Conservation Areas) Act 1990 section 17": 't',
    "Planning (Listed Buildings and Conservation Areas) Act 1990 section 2(2)": 't',
    "Planning (Listed Buildings and Conservation Areas) Act 1990 section 3": 't',
    "Planning (Listed Buildings and Conservation Areas) Act 1990 section 38": 't',
    "Planning (Listed Buildings and Conservation Areas) Act 1990 section 55(5D)": 't',
    "Planning (Listed Buildings and Conservation Areas) Act 1990 section 69(4)": 't',
    "Planning Act 2008 section 134(6A)": 't',
    "Planning Act 2008 section 170(5)": 't',
    "Planning Act 2008 section 205": 't',
    "Planning Act 2008 section 281(5)": 't',
    "Prevention of Damage by Pests Act 1949 section 4": 't',
    "Prevention of Damage by Pests Act 1949 section 7": 't',
    "Private Street Works Act 1892": 't',
    "Public Health (Drainage of Trade Premises) Act 1937 section 7": 't',
    "Public Health (Drainage of Trade Premises) Act 1937 section 7A": 't',
    "Public Health Act 1875 sub-section 23": 't',
    "Public Health Act 1875 sub-section 24": 't',
    "Public Health Act 1875 sub-section 26": 't',
    "Public Health Act 1936": 't',
    "Public Health Act 1936 section 138": 't',
    "Public Health Act 1936 section 24": 't',
    "Public Health Act 1936 section 275": 't',
    "Public Health Act 1936 section 29": 't',
    "Public Health Act 1936 section 291(1)": 't',
    "Public Health Act 1936 section 295": 't',
    "Public Health Act 1936 section 36": 't',
    "Public Health Act 1936 section 38": 't',
    "Public Health Act 1936 section 39": 't',
    "Public Health Act 1936 section 44": 't',
    "Public Health Act 1936 section 45": 't',
    "Public Health Act 1936 section 46": 't',
    "Public Health Act 1936 section 47": 't',
    "Public Health Act 1936 section 50": 't',
    "Public Health Act 1936 section 56": 't',
    "Public Health Act 1936 section 58": 't',
    "Public Health Act 1936 section 59": 't',
    "Public Health Act 1936 section 60": 't',
    "Public Health Act 1936 section 65(3)": 't',
    "Public Health Act 1936 section 75": 't',
    "Public Health Act 1936 section 83": 't',
    "Public Health Act 1936 section 95": 't',
    "Public Health Act 1936 section 96": 't',
    "Public Health Act 1961": 't',
    "Public Health Act 1961 section 12": 't',
    "Public Health Act 1961 section 17": 't',
    "Public Health Act 1961 section 46": 't',
    "Public Health Act 1961 section 73": 't',
    "Public Utilities and Street Works Act 1950": 't',
    "Regulatory Reform (Housing Assistance) (England and Wales) Order 2002": 't',
    "Requisitioned Land and War Works Act 1948 section 12": 't',
    "Rights of Light Act 1959 section 2(4)": 'f',
    "Small Dwellings Acquisition Act 1899": 't',
    "Thames Water Utilities Limited (Thames Tidway Tunnel) Order 2014, section 52(8)": 't',
    "Town and Country Planning (Control of Advertisements) (Amendment Number 2) regulations 1987 SI 1987/2227": 't',
    "Town and Country Planning (Control of Advertisements) (England) regulations 1960, regulations 23": 't',
    "Town and Country Planning (Control of Advertisements) (England) regulations 2007": 't',
    "Town and Country Planning (Control of Advertisements) (England) regulations 2007 SI 2007/783": 't',
    "Town and Country Planning (Control of Advertisements) regulations 1984 SI 1984/421": 't',
    "Town and Country Planning (Control of Advertisements) regulations 1987 SI 1987/804": 't',
    "Town and Country Planning (Control of Advertisements) regulations 1989 SI 1989/670": 't',
    "Town and Country Planning (Control of Advertisements) regulations 1992 SI 1992/666": 't',
    "Town and Country Planning (General Permitted Development) Order 1995": 't',
    "Town and Country Planning Act 1954 sub-section 28": 't',
    "Town and Country Planning Act 1954 sub-section 57": 't',
    "Town and Country Planning Act 1968": 't',
    "Town and Country Planning Act 1971": 't',
    "Town and Country Planning Act 1971 sub-section 158": 't',
    "Town and Country Planning Act 1971 sub-section 159": 't',
    "Town and Country Planning Act 1990": 't',
    "Town and Country Planning Act 1990 (section N/K)": 't',
    "Town and Country Planning Act 1990 schedule 9": 't',
    "Town and Country Planning Act 1990 section 102": 't',
    "Town and Country Planning Act 1990 section 106": 't',
    "Town and Country Planning Act 1990 section 110(4)": 't',
    "Town and Country Planning Act 1990 section 131": 't',
    "Town and Country Planning Act 1990 section 132": 't',
    "Town and Country Planning Act 1990 section 133": 't',
    "Town and Country Planning Act 1990 section 172": 't',
    "Town and Country Planning Act 1990 section 178(1)(b)": 't',
    "Town and Country Planning Act 1990 section 187A": 't',
    "Town and Country Planning Act 1990 section 198": 't',
    "Town and Country Planning Act 1990 section 201": 't',
    "Town and Country Planning Act 1990 section 202": 't',
    "Town and Country Planning Act 1990 section 215": 't',
    "Town and Country Planning Act 1990 section 70": 't',
    "Town and Country Planning Act 1990 section 97": 't',
    "Town and Country Planning General regulations 1992 section 219(1)": 't',
    "Transport and Works Act 1992 Part 1 section 14A(6)": 't',
    "Underground Works (London) Act 1956 section 6(9)": 't',
    "War Damage Act 1943 section 20": 't',
    "Water Industry Act 1991 section 104": 't',
    "Water Industry Act 1991 section 156": 't',
    "Water Industry Act 1991 section 158": 't',
    "Water Industry Act 1991 section 160": 't',
    "Water Industry Act 1991 section 66": 't',
    "Water Industry Act 1991 section 82": 't',
    "Water Resources Act 1991 section 95": 't',
    "Weeds Act 1959 section 3(3)": 't',
    "Wentworth Estate Act 1964": 't',
    "Wildlife and Countryside Act 1981 section 28": 't',
    "Wildlife and Countryside Act 1981 section 34": 't',
    "Wildlife and Countryside Act 1981 section 39": 't',
    "Yorkshire Water Authority Act 1986 section 41": 't'
}

instruments = [
    "Agreement",
    "Certificate",
    "Deed",
    "Direction",
    "List",
    "Notice",
    "Order",
    "Planning permission",
    "Resolution",
    "Scheme",
    "Transfer",
    "Undertaking"
]

mapping = {
    "Planning": {
        "display_order": 1,
        "permission": None,
        "display_name": "Planning",
        "sub_categories": {
            "Change a development": {
                "display_order": 1,
                "permission": None,
                "display_name": "Change a development",
                "statutory_provisions": [
                    "Town and Country Planning Act 1990 section 97"
                ],
                "instruments": [
                    "Order"
                ]
            },
            "Breach of conditions": {
                "display_order": 2,
                "permission": None,
                "display_name": "Breach of conditions",
                "statutory_provisions": [],
                "instruments": []
            },
            "Conservation area": {
                "display_order": 3,
                "permission": None,
                "display_name": "Conservation area",
                "statutory_provisions": ["Planning (Listed Buildings and Conservation Areas) Act 1990 section 69(4)"],
                "instruments": ["Notice"]
            },
            "Conditional planning consent": {
                "display_order": 4,
                "permission": None,
                "display_name": "Conditional planning consent",
                "statutory_provisions": ["Town and Country Planning Act 1990 section 70"],
                "instruments": ["Planning permission"]
            },
            "Enforcement notice": {
                "display_order": 5,
                "permission": None,
                "display_name": "Enforcement notice",
                "statutory_provisions": ["Town and Country Planning Act 1990 section 172"],
                "instruments": ["Notice"]
            },
            "Article 4": {
                "display_order": 6,
                "permission": None,
                "display_name": "Article 4",
                "statutory_provisions": ["Town and Country Planning (General Permitted Development) Order 1995"],
                "instruments": ["Direction"]
            },
            "No permitted development": {
                "display_order": 7,
                "permission": None,
                "display_name": "No permitted development",
                "statutory_provisions": [],
                "instruments": []
            },
            "Planning notices": {
                "display_order": 8,
                "permission": None,
                "display_name": "Planning notices",
                "statutory_provisions": [],
                "instruments": []
            },
            "Planning agreement": {
                "display_order": 9,
                "permission": None,
                "display_name": "Planning agreement",
                "statutory_provisions": ["Town and Country Planning Act 1990 section 106"],
                "instruments": ["Agreement"]
            },
            "Tree preservation order (TPO)": {
                "display_order": 10,
                "permission": None,
                "display_name": "Tree preservation order (TPO)",
                "statutory_provisions": [],
                "instruments": ["Order"]
            },
            "Listed building conditional planning consent": {
                "display_order": 11,
                "permission": None,
                "display_name": "Listed building conditional planning consent",
                "statutory_provisions": ["Planning (Listed Buildings and Conservation Areas) Act 1990 section 17"],
                "instruments": ["Deed"]
            },
        },
        "statutory_provisions": [],
        "instruments": []
    },
    "Financial": {
        "display_order": 2,
        "permission": None,
        "display_name": "Financial",
        "sub_categories": {},
        "statutory_provisions": [
            "Coast Protection Act 1949 section 8",
            "Coast Protection Act 1949 section 13",
            "Local Land Charges Act 1977 section 6(2)",
            "Anti-Social Behaviour Act 2003 section 77(3)",
            "Caravan Sites and Control of Development Act 1960 section 9(3)",
            "Community Infrastructure Levy Regulations 2010 regulation 66(1)",
            "Greater London Council (General Powers) Act 1973 section 28(b)",
            "Highways Act 1980 section 224",
            "Highways Act 1980 section 305",
            "London Building Acts (Amendment) At 1939 section 70(2)(a)",
            "Planning (Listed Buildings and Conservation Areas) Act 1990 section 55(5D)"
        ],
        "instruments": []
    },
    "Listed building": {
        "display_order": 3,
        "permission": None,
        "display_name": "Listed building",
        "sub_categories": {
            "Listed building": {
                "display_order": 1,
                "permission": None,
                "display_name": "Listed building",
                "statutory_provisions": ["Planning (Listed Buildings and Conservation Areas) Act 1990 section 2(2)"],
                "instruments": ["List"]
            },
            "Enforcement notice": {
                "display_order": 2,
                "permission": None,
                "display_name": "Enforcement notice",
                "statutory_provisions": [],
                "instruments": []
            },
            "Repairs notice": {
                "display_order": 3,
                "permission": None,
                "display_name": "Repairs notice",
                "statutory_provisions": [],
                "instruments": []
            }
        },
        "statutory_provisions": [],
        "instruments": []
    },
    "Land compensation": {
        "display_order": 4,
        "permission": None,
        "display_name": "Land compensation",
        "sub_categories": {},
        "statutory_provisions": [],
        "instruments": []
    },
    "Housing": {
        "display_order": 5,
        "permission": None,
        "display_name": "Housing",
        "sub_categories": {
            "Approval under house in multiple occupation (HMO)": {
                "display_order": 1,
                "permission": None,
                "display_name": "Approval under house in multiple occupation (HMO)",
                "statutory_provisions": [],
                "instruments": []
            },
            "Grant": {
                "display_order": 2,
                "permission": None,
                "display_name": "Grant",
                "statutory_provisions": [],
                "instruments": []
            },
            "Interim certificate under HMO": {
                "display_order": 3,
                "permission": None,
                "display_name": "Interim certificate under HMO",
                "statutory_provisions": [],
                "instruments": []
            },
            "Notice of works or repairs": {
                "display_order": 4,
                "permission": None,
                "display_name": "Notice of works or repairs",
                "statutory_provisions": [],
                "instruments": []
            },
            "Re-approval of grant": {
                "display_order": 5,
                "permission": None,
                "display_name": "Re-approval of grant",
                "statutory_provisions": [],
                "instruments": []
            },
            "Re-approval under HMO": {
                "display_order": 6,
                "permission": None,
                "display_name": "Re-approval under HMO",
                "statutory_provisions": [],
                "instruments": []
            }
        },
        "statutory_provisions": [],
        "instruments": []
    },
    "Light obstruction notice": {
        "display_order": 6,
        "permission": "Add LON",
        "display_name": "Light obstruction notice (LON)",
        "sub_categories": {},
        "statutory_provisions": [
            "Rights of Light Act 1959 section 2(4)"],
        "instruments": ["Certificate"]
    },
    "Other": {
        "display_order": 7,
        "permission": None,
        "display_name": "Other",
        "sub_categories": {
            "Ancient monuments": {
                "display_order": 1,
                "permission": None,
                "display_name": "Ancient monuments",
                "statutory_provisions": [
                    "Ancient Monuments and Archaeological Areas Act 1979 section 1(9)",
                    "Ancient Monuments and Archaeological Areas Act 1979 section 8(6)",
                    "Ancient Monuments and Archaeological Areas Act 1979 section 12(7)",
                    "Ancient Monuments and Archaeological Areas Act 1979 section 16(8)",
                    "Ancient Monuments and Archaeological Areas Act 1979 section 33(5)"
                ],
                "instruments": [
                    "Notice",
                    "Deed",
                    "Order"
                ]
            },
            "Assets of community value": {
                "display_order": 2,
                "permission": None,
                "display_name": "Assets of community value",
                "statutory_provisions": ["Localism Act 2011 section 100(a)"],
                "instruments": ["List"]
            },
            "Compulsory purchase order": {
                "display_order": 3,
                "permission": None,
                "display_name": "Compulsory purchase order",
                "statutory_provisions": [
                    "Acquisition of Land Act 1981 section 15(6)",
                    "Acquisition of Land Act 1981 schedule 1 paragraph 6",
                    "Planning Act 2008 section 134(6A)",
                    "New Towns Act 1981 section 12",
                    "Forestry Act 1967 Schedule 5 paragraph 2F",
                    "Transport and Works Act 1992 Part 1 section 14A(6)"
                ],
                "instruments": ["Order"]
            },
            "Highways": {
                "display_order": 4,
                "permission": None,
                "display_name": "Highways",
                "statutory_provisions": [],
                "instruments": []
            },
            "Smoke control order": {
                "display_order": 5,
                "permission": None,
                "display_name": "Smoke control order",
                "statutory_provisions": ["Clean Air Act 1993 section 18"],
                "instruments": ["Order"]
            },
            "Site of special scientific interest (SSSI)": {
                "display_order": 6,
                "permission": None,
                "display_name": "Site of special scientific interest (SSSI)",
                "statutory_provisions": ["Wildlife and Countryside Act 1981 section 28"],
                "instruments": ["Notice"]
            },
            "Licences": {
                "display_order": 7,
                "permission": None,
                "display_name": "Licences",
                "statutory_provisions": [],
                "instruments": []
            },
            "Local acts": {
                "display_order": 8,
                "permission": None,
                "display_name": "Local acts",
                "statutory_provisions": [],
                "instruments": []
            },
        },
        "statutory_provisions": [],
        "instruments": []
    }
}


def upgrade():

    load_stat_provision_data()
    load_instrument_data()

    for cat, cat_obj in mapping.items():
        parent_id = load_category(cat, cat_obj["display_order"], cat_obj["display_name"], None, cat_obj["permission"])
        for provision in cat_obj['statutory_provisions']:
            load_stat_provision_mapping(provision, parent_id)
        for instrument in cat_obj['instruments']:
            load_instrument_mapping(instrument, parent_id)
        for sub, sub_obj in cat_obj['sub_categories'].items():
            category_id = load_category(sub, sub_obj["display_order"], sub_obj["display_name"], parent_id, cat_obj["permission"])
            for provision in sub_obj['statutory_provisions']:
                load_stat_provision_mapping(provision, category_id)
            for instrument in sub_obj['instruments']:
                load_instrument_mapping(instrument, category_id)


def downgrade():
    query = "DELETE FROM charge_categories_stat_provisions;"
    op.execute(query)
    query = "DELETE FROM charge_categories_instruments;"
    op.execute(query)
    query = "DELETE FROM instruments;"
    op.execute(query)
    query = "DELETE FROM charge_categories;"
    op.execute(query)


def load_stat_provision_data():
    query = "DELETE FROM statutory_provision;"
    op.execute(query)

    for title, exclude in statutory_provisions.items():
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM statutory_provision WHERE title = '{0}') THEN INSERT INTO statutory_provision " \
                "(title, selectable) VALUES ('{0}', '{1}'); END IF; END $$;".format(title.replace("\'", "\'\'"), exclude)
        op.execute(query)


def load_instrument_data():
    for instrument in instruments:
        query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM instruments WHERE name = '{0}') THEN INSERT INTO instruments " \
                "(name) VALUES ('{0}'); END IF; END $$;".format(instrument)
        op.execute(query)


def load_category(name, display_order, display_name, parent_id, permission):
    if parent_id is None:
        parent_id = 'Null'
    if permission is None:
        permission = 'Null'
    else:
        permission = "'{}'".format(permission)
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM charge_categories WHERE name = '{0}' and parent_id = {3}) THEN " \
            "INSERT INTO charge_categories (name,  display_order, display_name, parent_id, permission) " \
            "VALUES ('{0}', {1}, '{2}', {3}, {4}); " \
            "END IF; END $$;".format(name, display_order, display_name, parent_id, permission)
    op.execute(query)

    conn = op.get_bind()
    if parent_id == 'Null':
        res = conn.execute(text("select id from charge_categories where name ='{0}' and parent_id is null".format(name, parent_id)))
    else:
        res = conn.execute(text("select id from charge_categories where name ='{0}' and parent_id = {1}".format(name, parent_id)))
    results = res.fetchall()
    return results[0][0]


def load_stat_provision_mapping(provision, category_id):
    conn = op.get_bind()
    res = conn.execute(text("select id from statutory_provision where title ='{0}'".format(provision.replace("\'", "\'\'"))))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Provision '{}' does not exits in the DB to be linked".format(provision))
    provision_id = results[0][0]
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM charge_categories_stat_provisions WHERE category_id = {0} AND statutory_provision_id = {1}) THEN " \
            "INSERT INTO charge_categories_stat_provisions (category_id, statutory_provision_id) " \
            "VALUES ({0}, {1}); " \
            "END IF; END $$;".format(category_id, provision_id)
    op.execute(query)


def load_instrument_mapping(instrument, category_id):
    conn = op.get_bind()
    res = conn.execute(text("select id from instruments where name ='{0}'".format(instrument)))
    results = res.fetchall()
    if results is None or len(results) == 0:
        raise Exception("Instrument '{}' does not exits in the DB to be linked".format(instrument))
    instrument_id = results[0][0]
    query = "DO $$ BEGIN IF NOT EXISTS (SELECT FROM charge_categories_instruments WHERE category_id = {0} AND instruments_id = {1}) THEN " \
            "INSERT INTO charge_categories_instruments (category_id, instruments_id) " \
            "VALUES ({0}, {1}); " \
            "END IF; END $$;".format(category_id, instrument_id)
    op.execute(query)
