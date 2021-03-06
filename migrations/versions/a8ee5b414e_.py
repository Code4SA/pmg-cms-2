"""empty message

Revision ID: a8ee5b414e
Revises: 270efdf57cc
Create Date: 2020-03-13 11:35:20.630010

"""

# revision identifiers, used by Alembic.
revision = 'a8ee5b414e'
down_revision = '270efdf57cc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('organisation_committee_organisation_id_key'), 'organisation_committee', ['organisation_id', 'committee_id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('organisation_committee_organisation_id_key'), 'organisation_committee', type_='unique')
    ### end Alembic commands ###
