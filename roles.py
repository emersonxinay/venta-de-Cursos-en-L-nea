from app import app, db, Usuario


def assign_role(correo, rol):
    with app.app_context():
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario:
            usuario.rol = rol
            db.session.commit()
            print(f"Rol '{rol}' asignado a {correo}.")
        else:
            print(f"Usuario con correo {correo} no encontrado.")


if __name__ == "__main__":
    correo = input("Ingrese el correo del usuario: ")
    rol = input("Ingrese el rol a asignar (admin/usuario): ")
    assign_role(correo, rol)
