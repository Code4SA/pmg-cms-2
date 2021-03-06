"""create bill_files table

Revision ID: 3d31ea243165
Revises: 32c9bf9a1bd8
Create Date: 2015-02-11 17:02:17.553921

"""

# revision identifiers, used by Alembic.
revision = '3d31ea243165'
down_revision = '32c9bf9a1bd8'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bill_files',
    sa.Column('bill_id', sa.Integer(), nullable=True),
    sa.Column('file_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.ForeignKeyConstraint(['file_id'], ['file.id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bill_files')
    ### end Alembic commands ###
