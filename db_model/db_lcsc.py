

from sqlalchemy import create_engine, Column, String, text, Text, TIMESTAMP
import contextlib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import INTEGER
from read_config import ReadConfig

config = ReadConfig()
db_setting = config.get_mysql_settings()
db_engine = create_engine(db_setting, pool_size=100, max_overflow=20, pool_timeout=100)
ModelBase = declarative_base()
DBsession = sessionmaker(bind=db_engine)


def db_lcsc_init():

    ModelBase.metadata.create_all(db_engine)
    print(ModelBase.metadata)
    print("Create table successfully!!!")


def check_table_exist(table_name):
    table_exist = db_engine.dialect.has_table(db_engine.connect(), table_name)
    if not table_exist:
        db_lcsc_init()
    else:
        print("table is exist!!!")


@contextlib.contextmanager
def get_session():
    s = DBsession()
    try:
        yield s
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()


class Electroncomponent(ModelBase):

    __tablename__ = 'electroncomponent'

    id = Column(INTEGER(unsigned=True), primary_key=True, comment='自增主键')
    Name = Column(String(100), nullable=False, default='', server_default='', comment='名称')
    Category = Column(String(100), nullable=False, default='', server_default='', comment='商品目录')
    Brand = Column(String(100), nullable=False, default='', server_default='', comment='品牌')
    Model = Column(String(100), nullable=False, default='', server_default='', comment='厂家型号')
    Code = Column(String(100), nullable=False, default='', server_default='', comment='商品编号')
    Encapsulating = Column(String(100), nullable=False, default='', server_default='', comment='封装')
    Weight = Column(String(100), nullable=False, default='', server_default='', comment='商品毛重')
    Package = Column(String(100), nullable=False, default='', server_default='', comment='包装方式')
    Unit = Column(String(100), nullable=False, default='', server_default='', comment='单位')
    Pdf = Column(String(500), nullable=False, default='', server_default='', comment='Pdf链接')
    SourceUrl = Column(String(255), nullable=False, default='', server_default='', comment='源网站信息链接')
    PriceSpec = Column(Text, comment='阶梯价格定义')
    AttributeList = Column(Text, comment='产品参数')
    ImageList = Column(Text, comment='标题图')
    create_at = Column(TIMESTAMP(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    update_at = Column(TIMESTAMP(True), nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='修改时间')

    __table_args__ = {
        "mysql_charset": "UTF8MB4",
        "mysql_collate": "utf8mb4_0900_ai_ci",
        "comment": "电子元件"
    }
