import re
from datetime import datetime
from typing import Any, List, Optional, Dict


def validate_required(value: Any, field_name: str) -> Optional[str]:
    if value is None or value == "":
        return f"El campo '{field_name}' es requerido"
    
    if isinstance(value, str) and value.strip() == "":
        return f"El campo '{field_name}' no puede estar vacío"
    
    return None


def validate_email(email: str) -> Optional[str]:
    if not email:
        return "Email no puede estar vacío"
    
    # Patrón básico para email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return "Formato de email inválido"
    
    return None


def validate_phone(phone: str) -> Optional[str]:
    if not phone:
        return "Teléfono no puede estar vacío"
    
    # Remover espacios y caracteres comunes
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Validar que contenga solo números y algunos caracteres especiales
    phone_pattern = r'^[\+]?[0-9]{8,15}$'
    
    if not re.match(phone_pattern, clean_phone):
        return "Formato de teléfono inválido (8-15 dígitos)"
    
    return None


def validate_length(value: str, min_len: int, max_len: int, field_name: str) -> Optional[str]:
    if not isinstance(value, str):
        return f"El campo '{field_name}' debe ser texto"
    
    length = len(value.strip())
    
    if length < min_len:
        return f"El campo '{field_name}' debe tener al menos {min_len} caracteres"
    
    if length > max_len:
        return f"El campo '{field_name}' no puede exceder {max_len} caracteres"
    
    return None


def validate_datetime(date_str: str, field_name: str = "fecha") -> Optional[str]:
    if not date_str:
        return f"El campo '{field_name}' es requerido"
    
    # Formatos aceptados
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M"
    ]
    
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return None
        except ValueError:
            continue
    
    return f"Formato de {field_name} inválido. Use: YYYY-MM-DD HH:MM:SS"


def validate_future_datetime(date_str: str, field_name: str = "fecha") -> Optional[str]:
    # Primero validar formato
    format_error = validate_datetime(date_str, field_name)
    if format_error:
        return format_error
    
    # Convertir a datetime
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S", 
        "%Y-%m-%dT%H:%M"
    ]
    
    parsed_date = None
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue
    
    if parsed_date and parsed_date <= datetime.now():
        return f"La {field_name} debe ser futura"
    
    return None


def validate_enum(value: str, allowed_values: List[str], field_name: str) -> Optional[str]:
    if value not in allowed_values:
        return f"El campo '{field_name}' debe ser uno de: {', '.join(allowed_values)}"
    
    return None


def validate_integer(value: Any, field_name: str, min_val: int = None, max_val: int = None) -> Optional[str]:
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        return f"El campo '{field_name}' debe ser un número entero"
    
    if min_val is not None and int_value < min_val:
        return f"El campo '{field_name}' debe ser mayor o igual a {min_val}"
    
    if max_val is not None and int_value > max_val:
        return f"El campo '{field_name}' debe ser menor o igual a {max_val}"
    
    return None


def collect_validation_errors(validations: List[Optional[str]]) -> List[str]:
    return [error for error in validations if error is not None]


def validate_fields_required(data: Dict, required_fields: List[str]) -> List[str]:
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Falta el campo requerido: '{field}'")
        else:
            error = validate_required(data[field], field)
            if error:
                errors.append(error)
    
    return errors

def validate_duenio_data(data: Dict) -> Dict[str, Any]:
    errors = []
    
    required_fields = ['nombre_apellido', 'telefono', 'email', 'direccion']
    
    required_errors = validate_fields_required(data, required_fields)
    errors.extend(required_errors)
    
    if required_errors:
        return {'is_valid': False, 'errors': errors}
    
    validations = [
        # nombre_apellido: max 100 chars
        validate_length(data['nombre_apellido'], 2, 100, 'nombre_apellido'),
        
        # telefono: max 20 chars, formato válido
        validate_length(data['telefono'], 8, 20, 'telefono'),
        validate_phone(data['telefono']),
        
        # email: max 100 chars, formato válido
        validate_length(data['email'], 5, 100, 'email'),
        validate_email(data['email']),
        
        # direccion: no vacía, max razonable
        validate_length(data['direccion'], 5, 500, 'direccion')
    ]
    
    # Recopilar errores
    validation_errors = collect_validation_errors(validations)
    errors.extend(validation_errors)
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_turno_data(data: Dict, duenio_exists_func=None) -> Dict[str, Any]:
    errors = []
    
    required_fields = ['nombre_mascota', 'fecha_turno', 'tratamiento', 'id_duenio']
    
    required_errors = validate_fields_required(data, required_fields)
    errors.extend(required_errors)
    
    if required_errors:
        return {'is_valid': False, 'errors': errors}
    
    estados_validos = ['pendiente', 'confirmado', 'completado', 'cancelado']
    
    validations = [
        # nombre_mascota: max 80 chars
        validate_length(data['nombre_mascota'], 1, 80, 'nombre_mascota'),
        
        # fecha_turno: formato datetime, debe ser futura
        validate_future_datetime(data['fecha_turno'], 'fecha_turno'),
        
        # tratamiento: no vacío, max razonable
        validate_length(data['tratamiento'], 3, 1000, 'tratamiento'),
        
        # id_duenio: entero válido, mayor que 0
        validate_integer(data['id_duenio'], 'id_duenio', min_val=1)
    ]
    
    # Validar estado si está presente (opcional en create, requerido en update)
    if 'estado' in data:
        estado_error = validate_enum(data['estado'], estados_validos, 'estado')
        if estado_error:
            validations.append(estado_error)
    
    # Recopilar errores de validación básica
    validation_errors = collect_validation_errors(validations)
    errors.extend(validation_errors)
    
    # Validar que el dueño existe (si se proporciona la función)
    if duenio_exists_func and len(errors) == 0:
        id_duenio = int(data['id_duenio'])
        if not duenio_exists_func(id_duenio):
            errors.append(f"No existe un dueño con ID: {id_duenio}")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_turno_update_data(data: Dict, duenio_exists_func=None) -> Dict[str, Any]:
    errors = []
    
    estados_validos = ['pendiente', 'confirmado', 'completado', 'cancelado']
    
    validations = []
    
    # Validar campos presentes
    if 'nombre_mascota' in data:
        validations.append(validate_length(data['nombre_mascota'], 1, 80, 'nombre_mascota'))
    
    if 'fecha_turno' in data:
        validations.append(validate_future_datetime(data['fecha_turno'], 'fecha_turno'))
    
    if 'tratamiento' in data:
        validations.append(validate_length(data['tratamiento'], 3, 1000, 'tratamiento'))
    
    if 'id_duenio' in data:
        validations.append(validate_integer(data['id_duenio'], 'id_duenio', min_val=1))
        
        # Validar existencia del dueño
        if duenio_exists_func:
            try:
                id_duenio = int(data['id_duenio'])
                if not duenio_exists_func(id_duenio):
                    errors.append(f"No existe un dueño con ID: {id_duenio}")
            except ValueError:
                errors.append("ID de dueño debe ser un número entero válido")
    
    if 'estado' in data:
        validations.append(validate_enum(data['estado'], estados_validos, 'estado'))
    
    # Recopilar errores
    validation_errors = collect_validation_errors(validations)
    errors.extend(validation_errors)
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }