# sbsTC
[![PyPI version]()]()

## Descripción
Obten el tipo de cambio oficial de la SBS (Perú). sbsTC es una libreria escrita en Python 3.11 que permite obtener de manera rápida y sencilla el tipo de cambio por día o rango de días.

## Instalación
```
pip install sbsTC
```

## Uso básico
```python
from sbsTC import SbsTC

tc = SbsTC()
data = tc.get_exchange('USD','25/09/2023','30/09/2023')
print(data)
```

### Obtendremos el siguiente resultado:
```python
{
    '25/09/2023': {'buy': '3.765', 'sell': '3.773'},
    '26/09/2023': {'buy': '3.779', 'sell': '3.787'},
    '27/09/2023': {'buy': '3.793', 'sell': '3.799'},
    '28/09/2023': {'buy': '3.801', 'sell': '3.806'},
    '29/09/2023': {'buy': '3.790', 'sell': '3.797'}
}
```

## Configuración
| Opción        | Descripción      | Predeterminado | Valores permitidos                         |
|:-------------:|:----------------:|:--------------:|:------------------------------------------:|
| `date_format` | Formato de fecha | `%d/%m/%Y`     | [http://strftime.org](http://strftime.org) |

## Ejemplo
```python
from sbsTC import SbsTC
tc = SbsTC(date_format='%Y-%m-%d')
data = tc.get_exchange('USD','25/09/2023')
print(data)
```
### Se obtiene el siguiente resultado:
```python
{'2023-09-25': {'buy': '3.765', 'sell': '3.773'}}
```

### En caso no encontrar información disponible:
```python
DataNotFound: No hay información disponible para el rango seleccionado
```


## Divisas
Listado de divisas permitidas

| Divisa           | Código |
|:----------------:|:------:|
| Dolar americano  | `USD`  |
| Euro             | `EUR`  |
| Yen Japones      | `JPY`  |
| Dolar canadiense | `CAD`  |
| Corona Sueca     | `SEK`  |
| Franco Suizo     | `CHF`  |
| Libra esterlina  | `GBP`  |

## Métodos

### get_exchange(`currency`,`from_date`,`to_date=None`)
Obtiene el tipo de cambio de la moneda enviada en base al rango de fecha ingresado. El resultado será un diccionario de tipos de cambio. ([https://docs.python.org/es/3/tutorial/datastructures.html#dictionaries](https://docs.python.org/es/3/tutorial/datastructures.html#dictionaries)).

## Consideraciones
* La información está disponible a partir del año 2000 en adelante.
* El tipo de cambio obtenido está con corte al día anterior.