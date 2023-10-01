import requests
from io import StringIO
from datetime import datetime
from .exceptions import InvalidCurrency, RequestsError, InvalidYearException, InvalidFormatDate, DataNotFound
import pandas as pd

class SbsTC:
    
    ENDPOINT = 'https://www.sbs.gob.pe/app/stats/seriesH-tipo_cambio_moneda_excel.asp'
    CURRENCIES = {
            'USD':'02'
        ,   'SEK':'55'
        ,   'CHF':'57'
        ,   'CAD':'11'
        ,   'EUR':'66'
        ,   'JPY':'38'
        ,   'GBP':'34'
    }
    FORMAT = '%d/%m/%Y'
    
    def __init__(self,date_format='%d/%m/%Y'):
        self.date_format = date_format
    
    def __get_currency(self,currency):
        try:
            return self.CURRENCIES[currency]
        except KeyError:
            raise InvalidCurrency(f'Invalid currency [{currency}]')
    
    def __get_request(self,parameters):
        try:
            r = requests.get(self.ENDPOINT,params=parameters)
            return StringIO(r.text)
        except Exception as e:
            raise RequestsError(str(e))
    
    @staticmethod
    def __valid_date(date):
        try:
            date = datetime.strptime(date,'%d/%m/%Y')
            if date.year < 2000:
                raise InvalidYearException('Information avaible from the 2000 year')
            return True
        except Exception as e:
            raise InvalidFormatDate(str(e))
    
    def __data_frame(self,currency,date,to_date):
        
        # valid dates
        self.__valid_date(date)
        self.__valid_date(to_date)
        
        # date
        from_date = datetime.strptime(date,'%d/%m/%Y')
        end_date  = datetime.strptime(to_date,'%d/%m/%Y')
        
        params = {
                "fecha1": from_date.strftime('%d/%m/%Y')
            ,   "fecha2": end_date.strftime('%d/%m/%Y')
            ,   "moneda": self.__get_currency(currency)
            ,   "cierre": ""
        }
        
        # data currency
        data_exchange = self.__get_request(params)
        dfs = pd.read_html(data_exchange, encoding='utf-8')
        
        if len(dfs[0]) <= 1:
            raise DataNotFound('No hay información disponible para el rango seleccionado')
        
        dfs[0].columns = dfs[0].iloc[0]
        dfs[0] = dfs[0][1:]
        df = dfs[0].drop('MONEDA', axis=1)
        if len(dfs[0])>0:
            data = df.to_dict(orient='dict')
        return data
        
    
    def get_exchange(self,currency,date,to_date=None):
        
        data = self.__data_frame(currency,date,to_date or date)
        
        exchanges = []
        for key,value in data['FECHA'].items():
            
            fecha = datetime.strptime(value,self.FORMAT).strftime(self.date_format)
            exchange = {
                fecha:{
                    'buy':data['COMPRA'][key],
                    'sell':data['VENTA'][key]
                }
            }
            exchanges.append(exchange)
        flattened_data = {}
        for entry in exchanges:
            for date, rates in entry.items():
                flattened_data[date] = rates
        
        return flattened_data

if __name__ == '__main__':
    today = datetime.today()
    dias = datetime.timedelta(days=5)
    fec_ini = (today - dias).strftime('%d/%m/%Y')
    fec_fin = today.strftime('%d/%m/%Y')
    tc  = SbsTC(date_format='%Y-%m-%d')
    data = tc.get_exchange('USD',fec_fin)
    print(data)