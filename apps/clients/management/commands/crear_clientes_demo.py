from django.core.management.base import BaseCommand
from apps.clients.models import Cliente
from apps.usuarios.models import Usuario
import random

class Command(BaseCommand):
    help = 'Crea 10 clientes de demostración con datos aleatorios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email del usuario para asignar los clientes',
            default='justinantonio2009@gmail.com'
        )

    def handle(self, *args, **kwargs):
        email = kwargs['email']
        
        # Obtener el usuario por email
        try:
            usuario = Usuario.objects.get(email=email)
            self.stdout.write(self.style.SUCCESS(f'✓ Usuario encontrado: {usuario.email}'))
        except Usuario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ No se encontró usuario con email: {email}'))
            self.stdout.write(self.style.WARNING('Usuarios disponibles:'))
            for u in Usuario.objects.all()[:5]:
                self.stdout.write(f'  - {u.email}')
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al obtener usuario: {e}'))
            return

        # Datos aleatorios para generar clientes
        nombres = [
            'María González', 'Carlos Rodríguez', 'Ana Martínez', 'Luis Fernández',
            'Carmen López', 'José García', 'Laura Sánchez', 'Miguel Torres',
            'Isabel Ramírez', 'Francisco Flores', 'Patricia Morales', 'Roberto Castro',
            'Elena Ortiz', 'Diego Ruiz', 'Sofía Mendoza', 'Andrés Vargas',
            'Valentina Cruz', 'Javier Herrera', 'Camila Jiménez', 'Daniel Reyes'
        ]

        empresas = [
            'Restaurante El Buen Sabor', 'Cafetería Central', 'Panadería La Espiga',
            'Supermercado San José', 'Farmacia Santa María', 'Librería El Estudiante',
            'Ferretería Industrial', 'Boutique Elegancia', 'Tecnología Avanzada S.A.',
            'Distribuidora Nacional', 'Comercial Los Andes', 'Importadora del Sur',
            'Servicios Profesionales', 'Construcciones Modernas', 'Alimentos Frescos'
        ]

        ciudades = [
            'Quito', 'Guayaquil', 'Cuenca', 'Ambato', 'Manta',
            'Portoviejo', 'Machala', 'Loja', 'Riobamba', 'Ibarra'
        ]

        grupos = ['regular', 'vip', 'corporativo']
        estados = ['activo', 'activo', 'activo', 'inactivo']  # Más activos
        creditos = [0, 15, 30, 45, 60, 90]

        clientes_creados = 0

        for i in range(10):
            try:
                # Generar datos aleatorios
                nombre = random.choice(nombres)
                empresa = random.choice(empresas) if random.random() > 0.3 else None
                
                # Generar cédula/RUC aleatorio (10 dígitos)
                identificacion = ''.join([str(random.randint(0, 9)) for _ in range(10)])
                
                # Generar teléfono (10 dígitos empezando con 09)
                telefono = '09' + ''.join([str(random.randint(0, 9)) for _ in range(8)])
                
                # Generar email
                email_base = nombre.lower().replace(' ', '.').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
                email = f"{email_base}@example.com"
                
                ciudad = random.choice(ciudades)
                direccion = f"Av. Principal {random.randint(100, 999)}, {ciudad}"
                
                grupo = random.choice(grupos)
                estado = random.choice(estados)
                credito = random.choice(creditos)
                
                # Generar cupo de crédito
                cupo = random.choice([0, 500, 1000, 2000, 5000, 10000]) if credito > 0 else 0
                
                # Generar descuento
                tasa_descuento = random.choice([0, 0, 0, 5, 10, 15])  # Más sin descuento
                
                # Crear cliente
                cliente = Cliente.objects.create(
                    usuario_creador=usuario,
                    codigo=f'CLI-{str(i+1).zfill(3)}',
                    nombre=nombre,
                    razon_social=empresa,
                    identificacion=identificacion,
                    email=email,
                    telefono=telefono,
                    direccion=direccion,
                    ciudad=ciudad,
                    grupo=grupo,
                    estado=estado,
                    credito=credito,
                    cupo=cupo,
                    tasa_descuento=tasa_descuento,
                    tasa_recargo=0,
                    comentarios=f'Cliente de demostración generado automáticamente.',
                    es_favorito=random.random() > 0.7  # 30% de probabilidad de ser favorito
                )
                
                clientes_creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Cliente creado: {cliente.nombre} ({cliente.identificacion})')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error al crear cliente {i+1}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Proceso completado: {clientes_creados}/10 clientes creados exitosamente')
        )
