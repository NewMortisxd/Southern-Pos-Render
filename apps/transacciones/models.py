from django.db import models, IntegrityError
from django.conf import settings
import time
import random
from django.utils import timezone

class Transaccion(models.Model):
    transaction_id = models.PositiveIntegerField(primary_key=True)
    factuID = models.PositiveIntegerField(editable=False)  # New field for user-specific ID
    numero_factura_usuario = models.PositiveIntegerField(editable=False)
    venta = models.ForeignKey('ventas.Venta', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario_creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    procesado_pago = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            max_retries = 10
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Generate a random transaction_id for global uniqueness
                    self.transaction_id = random.randint(100000, 999999)
                    
                    # Get the last factuID for this specific user
                    last_user_transaction = Transaccion.objects.filter(
                        usuario_creador=self.usuario_creador
                    ).order_by('-factuID').first()
                    
                    # Set factuID as sequential per user starting from 1
                    if last_user_transaction:
                        self.factuID = last_user_transaction.factuID + 1
                    else:
                        self.factuID = 1
                    
                    # Keep numero_factura_usuario for backward compatibility
                    self.numero_factura_usuario = self.factuID
                    
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    retry_count += 1
                    if retry_count >= max_retries:
                        # If we've tried too many times with random IDs, use a sequential approach
                        max_id = Transaccion.objects.aggregate(models.Max('transaction_id'))['transaction_id__max'] or 0
                        self.transaction_id = max_id + 1
                        
                        # Get the last factuID for this specific user
                        last_user_transaction = Transaccion.objects.filter(
                            usuario_creador=self.usuario_creador
                        ).order_by('-factuID').first()
                        
                        # Set factuID as sequential per user
                        if last_user_transaction:
                            self.factuID = last_user_transaction.factuID + 1
                        else:
                            self.factuID = 1
                        
                        # Keep numero_factura_usuario for backward compatibility
                        self.numero_factura_usuario = self.factuID
                            
                        super().save(*args, **kwargs)
                        break
                    time.sleep(0.1)
        else:
            # If transaction_id already exists, we don't modify factuID or numero_factura_usuario
            # to maintain the sequential numbering per user
            super().save(*args, **kwargs)
