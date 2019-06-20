import pytz
import datetime
from fixture import DataSet, NamedDataStyle, SQLAlchemyFixture

from pmg.models import db, House, Committee, CommitteeMeeting, Bill, BillType  # noqa

THIS_YEAR = datetime.datetime.today().year


class HouseData(DataSet):
    class joint:
        name = 'Joint (NA + NCOP)'
        name_short = 'Joint'
        sphere = 'national'

    class ncop:
        name = 'National Council of Provinces'
        name_short = 'NCOP'
        sphere = 'national'

    class na:
        name = 'National Assembly'
        name_short = 'NA'
        sphere = 'national'

    class president:
        name = 'The President\'s Office',
        name_short = 'President'
        sphere = 'national'


class CommitteeData(DataSet):
    class communications:
        name = 'Communications'
        house = HouseData.na
        premium = True

    class arts:
        name = 'Arts and Culture'
        house = HouseData.na


class CommitteeMeetingData(DataSet):
    class public:
        date = datetime.datetime(2016, 11, 5, 0, 0, 0, tzinfo=pytz.utc)
        title = 'Public meeting'
        committee = CommitteeData.arts

    class premium_recent:
        date = datetime.datetime(THIS_YEAR, 11, 5, 0, 0, 0, tzinfo=pytz.utc)
        title = 'Premium meeting recent'
        committee = CommitteeData.communications

    class premium_old:
        date = datetime.datetime(
            THIS_YEAR - 2, 11, 5, 0, 0, 0, tzinfo=pytz.utc)
        title = 'Premium meeting old'
        committee = CommitteeData.communications


class BillTypeData(DataSet):
    class section_74:
        name = "Section 74"
        prefix = "B"
        description = "Section 74"

    class section_77:
        name = "Section 77"
        prefix = "B"
        description = "Section 77"

    class private_member_bill_74:
        name = "Private Member Bill: S74"
        prefix = 'PMB'
        description = 'Private Member Bill: Section 74'

    class private_member_bill_77:
        name = 'Private Member Bill: S77'
        prefix = 'PMB'
        description = 'Private Member Bill: Section 77'


class BillData(DataSet):
    """
    Enter various types of bills
    """

    class food:
        year = 2019
        title = "Food and Health Bill"
        type = BillTypeData.section_74

    class farm:
        year = 2019
        title = 'Farm and Agricultural Bill'
        type = BillTypeData.section_77

    class public:
        year = 2019
        title = 'Public Investment Corporation Amendment Bill'
        type = BillTypeData.private_member_bill_74

    class child:
        year = 2019
        title = "Children's Amendment Bill"
        type = BillTypeData.private_member_bill_77


dbfixture = SQLAlchemyFixture(
    env=globals(),
    style=NamedDataStyle(),
    engine=db.engine,
    scoped_session=db.Session)
