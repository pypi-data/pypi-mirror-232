"""
包括mysqlOperator一个类

Classes
----------
mysqlOperator: mysql数据库操作， 包括创建table、添加列、新增数据、更新数据、查询数据

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_mysqlOperator import mysqlOperator

"""
import numpy as np
import pymysql  # PyMySQL==0.10.0
import pandas as pd  # pandas==1.1.0
import warnings
from ..decoraters import timer

# 设置print的最大显示行
pd.set_option("display.max.rows", None)
# 禁止打印时换行
pd.set_option("display.width", 3000)
# 设置print的最大显示列
pd.set_option("display.max.columns", 30)
# 禁止打印时换行
pd.set_option("display.width", 4000)
# 设置print的最大显示列
pd.set_option("display.max.columns", 200)
pd.set_option("display.max_colwidth", 200)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)


class mysqlOperator:
    """
    mysql数据库操作， 包括创建table、添加列、新增数据、更新数据、查询数据

    [1] 参数
    ----------
    databaseName:
        数据库名称，str，形如“bearing_pad_temper”
    tableName:
        数据表名称，str，形如“轴承瓦温20200320_20200327_原始数据”
    host:
        主机地址，str，optional， default， 'localhost'
    port:
        主机端口，int，optional， default， 3306
    userID:
        用户ID，str，optional， default， 'root'
    password:
        密码，str，optional， default， '000000'

    [2] 示例1
    --------
    >>> databaseName = 'bearing_pad_temper'
    >>> tableName = '轴承瓦温20200320_20200327_原始数据'
    >>> host = 'localhost'
    >>> port = 3306
    >>> userID = 'root'
    >>> password = '000000'
    >>> obj = mysqlOperator(databaseName=databaseName, tableName=tableName, host=host, port=port, userID=userID, password=password)
    >>> print(obj)
    """

    def __init__(self, **kwargs):
        self.dataBaseName = kwargs['databaseName']
        self.tableName = kwargs['tableName']
        self.host = kwargs['host'] if 'host' in kwargs.keys() else 'localhost'
        self.port = kwargs['port'] if 'port' in kwargs.keys() else 3306
        self.userID = kwargs['userID'] if 'userID' in kwargs.keys() else 'root'
        self.password = kwargs['password'] if 'password' in kwargs.keys() else '000000'
        self.__con__ = pymysql.connect(host=self.host, port=self.port, db=self.dataBaseName, user=self.userID,
                                       passwd=self.password,
                                       charset='utf8mb4')
        self.__cur__ = self.__con__.cursor()

    def createTable(self, **kwargs):
        """
        根据指定的 `tableName` 和 `columns` 创建 `dataTable`

        :key tableName: str, 表名;
        :key columns: dict, `key` 为 `COLUMN_Name` , `value` 为字段定义, 形如 {'timestamp':'TIMESTAMP null', 'col_1':'float null', 'col_2':'float null', 'col_3':'float null'}
        :return: dict, {'SQL语句': cmd}

        >>> data = obj.createTable(
        >>>     tableName="cache",
        >>>     columns={'timestamp':'TIMESTAMP null', 'col_1':'float null', 'col_2':'float null', 'col_3':'float null'}
        >>> )
        >>> print(data)
        """
        columns = kwargs['columns']
        columns_define = [f"{key} {columns[key]}" for key in columns.keys()]
        cmd = f"create table if not exists {kwargs['tableName']} ({', '.join(columns_define)})"
        self.__cur__.execute(cmd)
        self.__cur__.close()
        self.__con__.close()
        res = {
            'SQL语句': cmd
        }
        return res

    def addColumns(self, **kwargs):
        """
        根据指定的 `tableName` 和 `columns` 在已有数据表中添加列

        `columns` 中定义的新增列与现有字段不可重复, 否则全部不生效

        :key tableName: str, 表名
        :key columns: dict, `key` 为 `COLUMN_Name` , `value` 为字段定义, 形如 {'timestamp':'TIMESTAMP null', 'col_1':'float null', 'col_2':'float null', 'col_3':'float null'}
        :return: dict, {'SQL语句': cmd}

        >>> data = obj.addColumns(
        >>>     tableName="cache",
        >>>     columns={'timestamp3':'TIMESTAMP null', 'col_12':'float null', 'col_22':'float null', 'col_32':'float null'}
        >>> )
        """
        columns = kwargs['columns']
        columns_define = [f"{key} {columns[key]}" for key in columns.keys()]
        cmd = f"alter table {self.dataBaseName}.{kwargs['tableName']} add column ({', '.join(columns_define)})"
        self.__cur__.execute(cmd)
        self.__cur__.close()
        self.__con__.close()
        res = {
            'SQL语句': cmd
        }
        return res

    def dropColumns(self, **kwargs):
        """
        根据指定的 `tableName` 和 `columns` 在已有数据表中删除列

        `columns` 中定义的待删除列必须全部包括在现有字段中, 否则全部不生效


        :key tableName: str, 表名
        :key columns: list, 待删除字段名列表
        :return: dict, {'SQL语句': cmd}

        >>> data = obj.dropColumns(tableName="cache", columns=['col_1', 'timestamp44'])
        >>> print(data)
        """
        columns = kwargs['columns']
        cmd = f"alter table {self.dataBaseName}.{kwargs['tableName']} {', '.join([f'drop column {item}' for item in columns])}"
        self.__cur__.execute(cmd)
        self.__cur__.close()
        self.__con__.close()
        res = {
            'SQL语句': cmd
        }
        return res

    def execute(self, cmd):
        """
        执行sql命令

        :param cmd: str, SQL语句
        :return: dict, {'fetched': fetched, 'executeRes': res, 'SQL语句': cmd}
        """
        res = self.__cur__.execute(cmd)
        fetched = self.__cur__.fetchall()
        self.__cur__.close()
        self.__con__.close()
        return {
            'fetched': fetched,
            'executeRes': res,
            'SQL语句': cmd
        }

    def updateValue(self, **kwargs):
        """
        在数据表中按条件更新已有数据

        :key targetColumn: str, 待修改字段名
        :key targetValue: any, 待修改目标值
        :key condition: str, 修改条件, 形如 `col_5>0`
        :return: dict, {'SQL语句': cmd}

        >>> obj.updateValue(targetColumn="col_5", targetValue=-5, condition="col_5>0")
        """
        if "condition" in kwargs.keys():
            com = f"update {self.dataBaseName}.{self.tableName} set {kwargs['targetColumn']}={kwargs['targetValue']} where {kwargs['condition']}"
        else:
            com = f"update {self.dataBaseName}.{self.tableName} set {kwargs['targetColumn']}={kwargs['targetValue']}"
        self.__cur__.execute(com)
        self.__cur__.close()
        self.__con__.commit()
        self.__con__.close()
        res = {
            'SQL语句': com
        }
        return res

    @timer
    def writeDataframe(self, **kwargs):
        """
        将dataframe型数据录入mysql

        :key data: dataframe, 需要录入mysql的数据
        :return: dict, {'res': "写入完成"}

        >>> data = pd.DataFrame(np.random.randn(500000, colSize), columns=list(column_defines.keys()))
        >>> res = obj.writeDataframe(data=data)
        """
        if "data" not in kwargs.keys():
            warnings.warn("没有指定 dataframe 型的数据 data")
            exit(-1)
        df = kwargs["data"]
        res = self.execute(f"show columns from {self.dataBaseName}.{self.tableName};")
        valid = [item in (np.asarray(res['fetched'])[:, 0].tolist()) for item in df.columns]
        if not all(valid):
            _locs = [not item for item in valid]
            warnings.warn(f"不在{self.dataBaseName}.{self.tableName}中的字段有：{np.asarray(df.columns)[_locs]}")
            exit(-1)
        else:
            _columns = df.columns.tolist()
            _values = df.values.tolist()
            _values_str = [tuple([str(jtem) for jtem in item]) for item in _values]
            _cmd_group = []
            self.__cur__.executemany(
                f"insert into {self.tableName}({', '.join(_columns)}) values ({', '.join(['%s'] * len(_columns))})",
                _values_str)
            self.__con__.commit()
            self.__cur__.close()
            self.__con__.close()
            return {
                'res': "写入完成",
            }

    @timer
    def retrieveData(self, **kwargs):
        """
        根据查询数据的条件 `condition（控制时间）` 和 `content（所需查询的测点名称，使用','分隔）`

        :key content: str, 需要调用的列，默认为查询数据的样本数"count(*)"，形如 `"汽机润滑油冷油器出口总管油温1,发电机励端轴瓦温度"`
        :key condition: str，调用数据的条件，默认为全部数据，形如 `"(时间戳>=\'2020-03-20 16:18:03\') and (时间戳<=\'2020-03-20 16:18:11\')"`
        :return: dataframe or dict, df为调取的数据, 注意, 返回数据的列名称为 `content` 所指的名称列表， dict为查询结果

        >>> content = '汽机润滑油冷油器出口总管油温1,发电机励端轴瓦温度'
        >>> condition = "(时间戳>=\'2020-03-20 16:18:03\') and (时间戳<=\'2020-03-20 16:18:11\')"
        >>> obj = objectMySQL(databaseName='bearing_pad_temper', tableName='轴承瓦温20200320_20200327_原始数据')
        >>> data = obj.retrieveData(content=content, condition=condition)
        >>> print(data)
        """
        condition = kwargs['condition'] if 'condition' in kwargs.keys() else False
        content = kwargs['content'] if 'content' in kwargs.keys() else 'count(*)'

        com = None
        try:
            if condition:
                com = f"select {content} from {self.dataBaseName}.{self.tableName} where {kwargs['condition']}"
            else:
                com = f"select {content} from {self.dataBaseName}.{self.tableName}"
            self.__cur__.execute(com)
            res = self.__cur__.fetchall()
            self.__cur__.close()
            self.__con__.close()
        except Exception as e:
            warnings.warn(f"查询失败, SQL命令为 `{com}`")
            exit(-1)

        if content != 'count(*)':
            res = pd.DataFrame(res, columns=content.split(","))
        else:
            res = {
                '所查询数据量': [res[0][0]],
                'SQL语句': com
            }
        return res

    def inspect_Database_Table(self):
        """
        根据类定义查询 `databases` 和 `tables`

        >>> obj.inspect_Database_Table()
        """
        cmd = "show databases;"
        self.__cur__.execute(cmd)
        _res = [item[0] for item in self.__cur__.fetchall()]
        print("SQL Query:", cmd)
        print("Databases:", _res)
        print("=" * 20)

        cmd = f"show tables from {self.dataBaseName};"
        self.__cur__.execute(cmd)
        _res = [item[0] for item in self.__cur__.fetchall()]
        print("SQL Query:", cmd)
        print("Databases:", _res)
        print("=" * 20)

        cmd = f"show columns from {self.dataBaseName}.{self.tableName};"
        self.__cur__.execute(cmd)
        _res = [item[0] for item in self.__cur__.fetchall()]
        print("SQL Query:", cmd)
        print("Databases:", _res)
        print("=" * 20)

        cmd = f"describe {self.dataBaseName}.{self.tableName};"
        self.__cur__.execute(cmd)
        _array = np.array(self.__cur__.fetchall())
        _dict = {
            "Field": _array[:, 0], "Type": _array[:, 1], "Null": _array[:, 2],
            "Key": _array[:, 3], "Default": _array[:, 4], "Extra": _array[:, 5]}
        print("SQL Query:", cmd)
        print("Databases:\n", pd.DataFrame(_dict))
        self.__cur__.close()
        self.__con__.close()
