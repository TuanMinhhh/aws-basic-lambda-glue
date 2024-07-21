import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

from joblib import variables as V
from pyspark.sql import functions as F

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
print(args)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


#read data vietnamworks
s3_file_landing_vietnamwork = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/raw_zone/vnworks.json'
vietnamworks = spark.read.option('multiline', 'true').json(s3_file_landing_vietnamwork)

#read data topcv
s3_file_landing_topcv = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/raw_zone/topcv_selenium.json'
topcv = spark.read.option('multiline', 'true').json(s3_file_landing_topcv)

# logic transforms
#transforms date column topcv
regex_pattern_date_topcv = r"\d{2}/\d{2}/\d{4}"

topcv = topcv.withColumn('Hạn nộp',F.regexp_extract(F.col("Hạn nộp hồ sơ"),regex_pattern_date_topcv, 0)) \
             .withColumn("Deadline",F.date_format(F.to_date(F.col("Hạn nộp"), "dd/MM/yyyy"), "yyyy-MM-dd")) \
            .select('Job Title',
                    'Company Name',
                    'deadline',
                    'Mức lương',
                    'Mô tả công việc',
                    'Yêu cầu ứng viên',
                    'Quyền lợi',
                    'Địa điểm làm việc',
                    'Lĩnh vực',
                    'Url'
                    )


#transforms date column vietnamworks
regex_pattern_date_vnwork = r"\s\d+\s"

vietnamworks = vietnamworks.withColumn('deadline',F.regexp_extract(F.col("Hạn nộp hồ sơ"),regex_pattern_date_vnwork, 0).cast('int')) \
                    .select('Job Title',
                            'Company Name',
                            F.date_add(F.current_date(),F.col('Deadline')).alias('Deadline'),
                            'Mức lương',
                            'Mô tả công việc',
                            'Yêu cầu ứng viên',
                            'Quyền lợi',
                            'Địa điểm làm việc',
                            'Lĩnh vực',
                            'Url'
                            )

#union topcv and vietnamworks
df = topcv.unionAll(vietnamworks)
df = df.withColumn(
    'job_name',F.lower(F.col('Job Title'))) \
    .withColumn('job_description',F.lower(F.col('Mô tả công việc'))) \
    .withColumn('job_requirement',F.lower(F.col('Yêu cầu ứng viên'))) \
    .withColumn('benefit',F.lower(F.col('Quyền lợi'))) \
    .select('job_name','Company Name','Deadline','Mức lương','job_description','job_requirement','benefit','Địa điểm làm việc','Lĩnh vực','Url') \
    .cache()
    
    
#transforms job_title column
regex_pattern_job = r"data\s+\w+"

#them cot job_title moi
df_changed_job = df.withColumn(
        "role", 
        F.when(F.col("job_name").like("%ai%"), "ai engineer")
        .when(F.col('job_name').like('%phân tích dữ liệu%'), 'data analyst')
        .when(F.col('job_name').like('%data ana%'), 'data analyst')
        .when(F.col('job_name').like('%data engin%'), 'data engineer')
        .when(F.col('job_name').like('%data scie%'), 'data science')
        .otherwise(F.regexp_extract(F.col("job_name"),regex_pattern_job, 0))
        ) \
    .filter((F.col('role') != '') & (F.col('Mức lương') != 'N/A')) \
    .select('job_name','role','Company Name','Deadline','Mức lương','job_description','job_requirement','benefit','Địa điểm làm việc','Lĩnh vực','Url')
    
    
#tao keywords de quet noi dung
keywords = [
    "bigquery", "r", "warehouse", "etl", "python", "spark", "cloud", "sql", "hadoop", "aws", "database", "java",
    "tableau", "excel", "pipeline", "oracle", "csdl", "nosql", "powerbi", "azure", "kafka", "visualization", "scala",
    "warehousing", "apache", "databases", "ci/cd", "mysql", "airflow", "pentaho", "docker", "glue", "nifi", "rdbms",
    "postgresql", "redshift", "tensorflow", "mongodb", "bigdata", "s3", "pytorch", "dashboard", "power", "pyclustering"\
]

#nối chuỗi job_description và job_requirement
df_concat = df_changed_job.withColumn("concat_string",F.concat(F.col('job_requirement'), F.lit(' '), F.col('job_description')))

#loại bỏ các ký tự không phải chữ và số
df_cleaned = df_concat.withColumn("clean_concat_string", F.regexp_replace(F.col("concat_string"), "[-|:|.|,|(|)|;]", " "))

# Tách các từ trong cột `clean_concat_string`
df_words = df_cleaned.withColumn("word", F.explode(F.split(F.col("clean_concat_string"), "\\s+")))

# Tạo một cột chứa danh sách keyword có trong phần description và requirement
df_keywords = df_words.filter(F.col("word").isin(keywords)) \
    .groupBy('job_name','role','Company Name','Deadline','Mức lương','job_description','job_requirement','benefit','Địa điểm làm việc','Lĩnh vực','Url') \
    .agg(F.array_distinct(F.collect_list("word")).alias("keywords")) \
    .select('url','keywords')

#join với df_changed_job do nhiều job không chứa keywords
df_keywords = df_changed_job.alias('t1') \
    .join(df_keywords.alias('t2'), df_changed_job.Url == df_keywords.url,'left') \
    .select('job_name','role','Company Name','Deadline','Mức lương','job_description','job_requirement','benefit','Địa điểm làm việc','Lĩnh vực','t1.Url','t2.keywords')


#Tu cot dia diem lam viec --> tao cot chi lay ten thanh pho
ha_noi = ["Hà Nội", "Ha Noi", "HaNoi", "HN"]
tp_hcm = ["Hồ Chí Minh", "Ho Chi Minh", "HCM", "District"]

# Create a regular expression pattern from the list
regex_ha_noi = "|".join(ha_noi)
regex_tp_hcm = "|".join(tp_hcm)

df_city = df_keywords.withColumn(
                        'City',
                        F.when(F.col('Địa điểm làm việc').rlike(regex_ha_noi),'Hà Nội')
                        .when(F.col('Địa điểm làm việc').rlike(regex_tp_hcm),'TP Hồ Chí Minh')
                        .otherwise('Khác')
                        ) \
                    .select('job_name','role','Company Name','Deadline','Mức lương','job_description','job_requirement','benefit','Địa điểm làm việc','City','Lĩnh vực','t1.Url','keywords')
    
df_final = df_city.withColumnRenamed('Company Name', 'company') \
                  .withColumnRenamed('Mức lương','salary') \
                  .withColumnRenamed('Địa điểm làm việc','location') \
                  .withColumnRenamed('Lĩnh vực','field')

#write to s3 bucket
s3_saving_path = f's3://{V.DATA_LANDING_BUCKET_NAME}/minhpt1_test/golden_zone/job_detail'

df_final.coalesce(1).write.mode('overwrite').parquet(s3_saving_path)
job.commit()