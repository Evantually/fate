"""added description text and item quality

Revision ID: 917cea184c6e
Revises: 10c08e8fb19e
Create Date: 2019-10-17 00:45:03.563979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '917cea184c6e'
down_revision = '10c08e8fb19e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('description_text',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=128), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['profession_item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('profession_ingredient', sa.Column('item_quality', sa.String(length=64), nullable=True))
    op.add_column('profession_ingredient', sa.Column('item_type', sa.String(length=64), nullable=True))
    op.add_column('profession_item', sa.Column('armor_class', sa.String(length=64), nullable=True))
    op.add_column('profession_item', sa.Column('item_quality', sa.String(length=64), nullable=True))
    op.add_column('profession_item', sa.Column('item_slot', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profession_item', 'item_slot')
    op.drop_column('profession_item', 'item_quality')
    op.drop_column('profession_item', 'armor_class')
    op.drop_column('profession_ingredient', 'item_type')
    op.drop_column('profession_ingredient', 'item_quality')
    op.drop_table('description_text')
    # ### end Alembic commands ###
