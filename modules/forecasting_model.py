import pandas as pd
import numpy as np
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import warnings

# Suprime warnings desnecessários dos modelos
warnings.filterwarnings('ignore')

# Configura o logger para este módulo
logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """
    Classe base abstrata para todos os modelos de previsão.
    """
    
    @abstractmethod
    def predict(self, data: pd.DataFrame, horizonte: int, **params) -> pd.DataFrame:
        """
        Executa a previsão para o horizonte especificado.
        
        Args:
            data (pd.DataFrame): DataFrame com colunas 'data' e 'valor'
            horizonte (int): Número de períodos a prever
            **params: Parâmetros específicos do modelo
        
        Returns:
            pd.DataFrame: DataFrame com colunas 'data_previsao', 'valor_previsto', 
                         'limite_inferior', 'limite_superior'
        """
        pass

class ArimaModel(BaseModel):
    """
    Implementa previsão usando modelo ARIMA.
    """
    
    def predict(self, data: pd.DataFrame, horizonte: int, **params) -> pd.DataFrame:
        """
        Executa previsão ARIMA.
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            logger.info(f"Executando previsão ARIMA para {horizonte} períodos")
            
            # Parâmetros padrão
            p = params.get('p', 1)
            d = params.get('d', 1)
            q = params.get('q', 1)
            
            # Prepara os dados
            ts = data.set_index('data')['valor']
            
            # Treina o modelo
            model = ARIMA(ts, order=(p, d, q))
            fitted_model = model.fit()
            
            # Faz a previsão
            forecast = fitted_model.get_forecast(steps=horizonte)
            forecast_mean = forecast.predicted_mean
            forecast_ci = forecast.conf_int()
            
            # Gera as datas futuras
            last_date = data['data'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                       periods=horizonte, freq='D')
            
            # Monta o DataFrame de resultado
            result = pd.DataFrame({
                'data_previsao': future_dates,
                'valor_previsto': forecast_mean.values,
                'limite_inferior': forecast_ci.iloc[:, 0].values,
                'limite_superior': forecast_ci.iloc[:, 1].values
            })
            
            logger.info("Previsão ARIMA concluída com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro na previsão ARIMA: {e}")
            raise

class ProphetModel(BaseModel):
    """
    Implementa previsão usando modelo Prophet.
    """
    
    def predict(self, data: pd.DataFrame, horizonte: int, **params) -> pd.DataFrame:
        """
        Executa previsão Prophet.
        """
        try:
            from prophet import Prophet
            
            logger.info(f"Executando previsão Prophet para {horizonte} períodos")
            
            # Prepara os dados no formato do Prophet
            prophet_data = data.rename(columns={'data': 'ds', 'valor': 'y'})
            
            # Parâmetros do modelo
            growth = params.get('growth', 'linear')
            seasonality_mode = params.get('seasonality_mode', 'additive')
            
            # Treina o modelo
            model = Prophet(growth=growth, seasonality_mode=seasonality_mode)
            model.fit(prophet_data)
            
            # Cria o DataFrame de datas futuras
            future = model.make_future_dataframe(periods=horizonte)
            
            # Faz a previsão
            forecast = model.predict(future)
            
            # Extrai apenas as previsões futuras
            future_forecast = forecast.tail(horizonte)
            
            # Monta o DataFrame de resultado
            result = pd.DataFrame({
                'data_previsao': future_forecast['ds'].values,
                'valor_previsto': future_forecast['yhat'].values,
                'limite_inferior': future_forecast['yhat_lower'].values,
                'limite_superior': future_forecast['yhat_upper'].values
            })
            
            logger.info("Previsão Prophet concluída com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro na previsão Prophet: {e}")
            raise

class RandomForestModel(BaseModel):
    """
    Implementa previsão usando modelo RandomForest.
    """
    
    def predict(self, data: pd.DataFrame, horizonte: int, **params) -> pd.DataFrame:
        """
        Executa previsão RandomForest.
        """
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            logger.info(f"Executando previsão RandomForest para {horizonte} períodos")
            
            # Parâmetros do modelo
            n_estimators = params.get('n_estimators', 100)
            max_depth = params.get('max_depth', 10)
            random_state = params.get('random_state', 42)
            
            # Prepara os dados para aprendizado supervisionado
            X, y = self._create_features(data)
            
            # Treina o modelo
            model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state
            )
            model.fit(X, y)
            
            # Faz previsões iterativas
            predictions = []
            confidence_intervals = []
            
            # Usa os últimos valores como ponto de partida
            last_values = data['valor'].tail(5).values  # Últimos 5 valores como features
            last_date = data['data'].max()
            
            for i in range(horizonte):
                # Cria features para a previsão
                current_date = last_date + timedelta(days=i+1)
                features = self._create_single_prediction_features(last_values, current_date)
                
                # Faz a previsão
                pred = model.predict([features])[0]
                predictions.append(pred)
                
                # Calcula intervalo de confiança usando as árvores individuais
                tree_predictions = [tree.predict([features])[0] for tree in model.estimators_]
                ci_lower = np.percentile(tree_predictions, 2.5)
                ci_upper = np.percentile(tree_predictions, 97.5)
                confidence_intervals.append((ci_lower, ci_upper))
                
                # Atualiza os últimos valores para a próxima iteração
                last_values = np.append(last_values[1:], pred)
            
            # Gera as datas futuras
            future_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                       periods=horizonte, freq='D')
            
            # Monta o DataFrame de resultado
            result = pd.DataFrame({
                'data_previsao': future_dates,
                'valor_previsto': predictions,
                'limite_inferior': [ci[0] for ci in confidence_intervals],
                'limite_superior': [ci[1] for ci in confidence_intervals]
            })
            
            logger.info("Previsão RandomForest concluída com sucesso")
            return result
            
        except Exception as e:
            logger.error(f"Erro na previsão RandomForest: {e}")
            raise
    
    def _create_features(self, data: pd.DataFrame):
        """
        Cria features para o modelo RandomForest.
        """
        # Cria lags (valores passados)
        lag_features = []
        target = []
        
        for i in range(5, len(data)):  # Usa 5 lags
            # Features: últimos 5 valores + features de data
            lags = data['valor'].iloc[i-5:i].values
            date_features = self._extract_date_features(data['data'].iloc[i])
            features = np.concatenate([lags, date_features])
            
            lag_features.append(features)
            target.append(data['valor'].iloc[i])
        
        return np.array(lag_features), np.array(target)
    
    def _create_single_prediction_features(self, last_values, date):
        """
        Cria features para uma única previsão.
        """
        date_features = self._extract_date_features(date)
        return np.concatenate([last_values, date_features])
    
    def _extract_date_features(self, date):
        """
        Extrai features da data.
        """
        return np.array([
            date.month,
            date.day,
            date.weekday(),
            date.year % 100  # Últimos 2 dígitos do ano
        ])

def forecast_factory(modelo_nome: str) -> BaseModel:
    """
    Fábrica de modelos de previsão.
    
    Args:
        modelo_nome (str): Nome do modelo ('ARIMA', 'Prophet', 'RandomForest')
    
    Returns:
        BaseModel: Instância do modelo solicitado
    
    Raises:
        ValueError: Se o modelo não for suportado
    """
    modelos = {
        "ARIMA": ArimaModel(),
        "Prophet": ProphetModel(),
        "RandomForest": RandomForestModel()
    }
    
    modelo = modelos.get(modelo_nome)
    if not modelo:
        logger.error(f"Modelo '{modelo_nome}' não suportado")
        raise ValueError(f"Modelo '{modelo_nome}' não suportado. Modelos disponíveis: {list(modelos.keys())}")
    
    logger.info(f"Modelo {modelo_nome} instanciado com sucesso")
    return modelo

