"""Agregar fecha de expiracion de cursos comprados

Revision ID: 1f301c9fbb48
Revises: a2442f27d56f
Create Date: 2025-01-22 17:47:33.927184

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta


# revision identifiers, used by Alembic.
revision = '1f301c9fbb48'
down_revision = 'a2442f27d56f'
branch_labels = None
depends_on = None


def upgrade():
    # Agregar la columna con un valor por defecto
    op.add_column('venta', sa.Column(
        'fecha_expiracion', sa.DateTime(), nullable=True))

    # Establecer un valor por defecto para los registros existentes
    default_expiration = datetime.utcnow() + timedelta(days=30)
    op.execute(f"UPDATE venta SET fecha_expiracion = '{default_expiration}' WHERE fecha_expiracion IS NULL")

    # Hacer la columna no nula
    op.alter_column('venta', 'fecha_expiracion', nullable=False)

def downgrade():
    # Eliminar la columna en caso de downgrade
    op.drop_column('venta', 'fecha_expiracion')

    # ### end Alembic commands ###
