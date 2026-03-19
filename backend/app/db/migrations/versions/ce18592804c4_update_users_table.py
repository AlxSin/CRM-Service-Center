from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ce18592804c4'
down_revision = 'b2455dbf4556'
branch_labels = None
depends_on = None

def upgrade():
    # 1. Создаём ENUM вручную
    userrole = sa.Enum('admin', 'manager', 'technician', 'user', name='userrole')
    userrole.create(op.get_bind(), checkfirst=True)

    # 2. Добавляем колонку
    op.add_column('users', sa.Column('role', userrole, nullable=False, server_default='user'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')))

    # 3. Удаляем старую колонку
    op.drop_column('users', 'is_superuser')


def downgrade():
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=True))

    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'role')

    # Удаляем ENUM
    userrole = sa.Enum(name='userrole')
    userrole.drop(op.get_bind(), checkfirst=True)
