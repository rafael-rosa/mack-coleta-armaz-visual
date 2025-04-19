# SOLUÇÃO PARA COLETA, ARMAZENAMENTO, VISUALIZAÇÃO E MONITORAMENTO DE INDICADORES FINANCEIROS

## Proposta de problema
Uma solução para coleta de dados do mercado financeiro a partir de diversas origens e que permita a apresentação destes indicadores de forma prática e de fácil customização. A solução também deve permitir a criação de “thresholds”, alertas e deve ser escalável.

---

## 🚀 Instruções de Uso

Login Airflow (http://localhost:8080/login/): airflow/airflow

Login Grafana (http://localhost:3000/login): admin/admin

Login base de dados (jdbc:postgresql://localhost:5432/postgres): postgres/1234

### 🛠️ Setup do Ambiente

1. Navegue até a pasta do projeto:
   ```bash
   cd airflow-docker
   docker compose up airflow-init
   docker compose up
2. Executar a DAG "dag_proj_hist_btc" no Airflow
3. Criar o Dashboard no Grafana importando o arquivo "dashboard_grafana.json"
4. Criar o alerta de cotacao do Dolar no Grafana importando o arquivo "alerta_dolar_grafana.yaml"
