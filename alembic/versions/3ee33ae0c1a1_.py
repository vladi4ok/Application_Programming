"""empty message

Revision ID: 3ee33ae0c1a1
Revises: 
Create Date: 2022-02-17 22:51:41.140333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ee33ae0c1a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('UserName', sa.String(length=45), nullable=False),
    sa.Column('firstName', sa.String(length=45), nullable=False),
    sa.Column('lastName', sa.String(length=45), nullable=False),
    sa.Column('email', sa.String(length=45), nullable=False),
    sa.Column('phone', sa.String(length=45), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('UserName'),
    sa.UniqueConstraint('UserName'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('Account',
    sa.Column('AccountNumber', sa.Integer(), nullable=False),
    sa.Column('balance', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('currencyCode', sa.String(length=45), nullable=False),
    sa.Column('UserName', sa.String(length=45), nullable=False),
    sa.ForeignKeyConstraint(['UserName'], ['User.UserName'], ),
    sa.PrimaryKeyConstraint('AccountNumber'),
    sa.UniqueConstraint('AccountNumber')
    )
    op.create_table('Transfer',
    sa.Column('idTransfer', sa.Integer(), nullable=False),
    sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
    sa.Column('currencyCode', sa.String(length=45), nullable=False),
    sa.Column('fromAccountNumber', sa.Integer(), nullable=False),
    sa.Column('toAccountNumber', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['fromAccountNumber'], ['Account.AccountNumber'], ),
    sa.ForeignKeyConstraint(['toAccountNumber'], ['Account.AccountNumber'], ),
    sa.PrimaryKeyConstraint('idTransfer'),
    sa.UniqueConstraint('idTransfer')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Transfer')
    op.drop_table('Account')
    op.drop_table('User')
    # ### end Alembic commands ###
