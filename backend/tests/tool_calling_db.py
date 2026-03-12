import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.agents import test_agent
from src.tools.sql_db import get_db_schema, query_db
from src.tools import get_user_info
from src.tools.chart import generate_chart


if __name__ == "__main__":
    session_id = 'test_tool'
    user_id = 'zein18'
    agent = test_agent(
        session_id=session_id, user_id=user_id, tools=[get_db_schema, query_db, generate_chart, get_user_info]
    )
    agent.state.set("session_id",session_id)
    agent.state.set("user_id",user_id)


    # agent call
    # question = 'hi, kamu ada info apa aja?'
    # question = 'ada berapa jumlah city?'
    # question = 'ada berapa jumlah product yang mendapatkan rating 1-5? grouping dan buat visualisasinya'
    # result = agent(question)
    # token_data = result.metrics.accumulated_usage
    # agent_metrics = result.metrics.accumulated_metrics
    # print(f"token_data: {token_data}")
    # print(f"agent_metrics: {agent_metrics}")


    # direct tool call
    result = agent.tool.get_user_info()
    # result = agent.tool.get_db_schema()
    # sql = """
    #     SELECT
    #         to_char(order_purchase_timestamp::timestamp, 'YYYY-MM') AS month,
    #         count(*) AS total_orders,
    #         round(sum(p.payment_value)::numeric, 2) AS total_revenue
    #     FROM olist_orders_dataset o
    #     JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
    #     GROUP BY month
    #     ORDER BY month DESC
    #     LIMIT 10
    #     """
    # result = agent.tool.query_db(query=sql)
    # data =  "[{\"month\": \"2018-10\", \"total_orders\": 4, \"total_revenue\": \"589.67\"}, {\"month\": \"2018-09\", \"total_orders\": 16, \"total_revenue\": \"4439.54\"}, {\"month\": \"2018-08\", \"total_orders\": 6698, \"total_revenue\": \"1022425.32\"}, {\"month\": \"2018-07\", \"total_orders\": 6507, \"total_revenue\": \"1066540.75\"}, {\"month\": \"2018-06\", \"total_orders\": 6419, \"total_revenue\": \"1023880.50\"}, {\"month\": \"2018-05\", \"total_orders\": 7135, \"total_revenue\": \"1153982.15\"}, {\"month\": \"2018-04\", \"total_orders\": 7209, \"total_revenue\": \"1160785.48\"}, {\"month\": \"2018-03\", \"total_orders\": 7512, \"total_revenue\": \"1159652.12\"}, {\"month\": \"2018-02\", \"total_orders\": 6952, \"total_revenue\": \"992463.34\"}, {\"month\": \"2018-01\", \"total_orders\": 7563, \"total_revenue\": \"1115004.18\"}]"
    # result = agent.tool.generate_chart(
    #         data="[{\"service\": \"Amazon RDS\", \"cost\": 825.37}, {\"service\": \"Amazon OpenSearch Service\", \"cost\": 179.03}, {\"service\": \"Amazon EC2 (Compute)\", \"cost\": 155.64}, {\"service\": \"Tax\", \"cost\": 137.39}, {\"service\": \"EC2 - Other\", \"cost\": 70.48}, {\"service\": \"Amazon VPC\", \"cost\": 11.16}, {\"service\": \"Amazon SageMaker\", \"cost\": 5.60}, {\"service\": \"Amazon Bedrock\", \"cost\": 0.92}, {\"service\": \"AWS Secrets Manager\", \"cost\": 0.40}, {\"service\": \"Claude 3.5 Sonnet (Bedrock)\", \"cost\": 0.25}, {\"service\": \"AmazonCloudWatch\", \"cost\": 0.18}, {\"service\": \"Amazon Redshift\", \"cost\": 0.04}, {\"service\": \"Claude 3 Haiku (Bedrock)\", \"cost\": 0.02}, {\"service\": \"AWS Cost Explorer\", \"cost\": 0.02}, {\"service\": \"Amazon Simple Storage Service\", \"cost\": 0.01}]",
    #         chart_type="pie",
    #         y_columns="cost",
    #         x_column="service",
    #         show_legend=True,
    #         show_values=True,
    #         title="Negara dengan Pembeli Tertinggi"
    # )
    print(result)
    # data = json.loads(result['content'][0]['text'])
    # print(json.dumps(data, indent=2))