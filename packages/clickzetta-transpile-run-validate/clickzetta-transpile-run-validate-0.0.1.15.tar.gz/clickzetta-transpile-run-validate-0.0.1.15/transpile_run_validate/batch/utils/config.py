import json
from clickzetta import connect


class Config():
    def __init__(self, conf_file='config.json'):
        print(f'read {conf_file}')
        with open(conf_file) as f:
            config = json.load(f)
        # clickzetta
        cz_conf = config['clickzetta']
        self.username = cz_conf['username']
        self.password = cz_conf['password']
        self.instance = cz_conf['instance']
        self.service = cz_conf['service']
        self.workspace = cz_conf['workspace']
        self.schema = cz_conf['schema']
        self.vcluster = cz_conf['vcluster']
        # hints
        self.hints = config['hints']

    def get_cz_conn(self):
        conn = connect(username=self.username,
                       password=self.password,
                       service=self.service,
                       instance=self.instance,
                       workspace=self.workspace,
                       schema=self.schema,
                       vcluster=self.vcluster)
        return conn

    def get_hints(self):
        return {'hints': self.hints}
