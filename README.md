*HACKATON CI/CD 07/30/2025*
BY: Jorge Valdez y Angel Valadez
# Django CI
 
Este proyecto implementa un pipeline de integración continua (CI) para una aplicación Django utilizando **GitHub Actions**. El flujo automatiza la instalación de dependencias, pruebas y despliegue en AWS S3, asegurando calidad y entrega continua con buenas prácticas de seguridad.
 
---
 
## Descripción del pipeline
 
El pipeline está configurado para ejecutarse automáticamente ante *push* o *pull request* hacia la rama `main`. Incluye dos trabajos principales:
 
1. **build**  
   - Corre sobre Ubuntu.
   - Configura Python (versión 3.x).
   - Instala dependencias desde `application/requirements.txt`.
   - (Idealmente, aquí podrían añadirse pasos para ejecutar linting, pruebas unitarias y escaneo de seguridad).
 
2. **deploy-s3**  
   - Se ejecuta después de que `build` finaliza con éxito.
   - Configura credenciales de AWS usando secretos almacenados en GitHub Secrets.
   - Sincroniza el contenido de la carpeta `application` con un bucket S3 (`bucket-hackathon-lexisnexis`).
   - Se asegura de eliminar archivos en S3 que ya no están presentes localmente.
 
---
 
## Capturas relevantes
 
### Pipeline en ejecución en GitHub Actions  
<img width="763" height="758" alt="image" src="https://github.com/user-attachments/assets/6c9b8046-5e10-41be-87e8-ff59d96ebcd5" />
 
### Despliegue exitoso en S3  
<img width="1615" height="655" alt="image" src="https://github.com/user-attachments/assets/309ddc09-b928-40e4-92d0-5d0e833d037e" />
<img width="1902" height="796" alt="Captura de pantalla 2025-07-30 155958" src="https://github.com/user-attachments/assets/61c1987d-f33d-4e03-b391-3347997887eb" />

 
### Uso de GitHub Secrets para seguridad  
<img width="1021" height="814" alt="image" src="https://github.com/user-attachments/assets/9b3ec398-7853-4ba5-bac5-a4144079f175" />

---
 
## Buenas prácticas de seguridad
 
- Las credenciales AWS nunca se almacenan en texto plano ni en el repositorio.
- Se usan GitHub Secrets para inyectar las credenciales en tiempo de ejecución.
- El bucket S3 está configurado para solo aceptar despliegues autorizados desde CI.
- Se recomienda agregar escaneo automático de vulnerabilidades y pruebas para mayor robustez.
 



