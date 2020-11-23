import time, os, json

'''
运行前请依据文件名和节点数，修改__init__函数中的文件名和节点数
'''


class BcdChecker:
    def __init__(self):
        self.filename = 'Test.json'  # 文件名
        self.num_nodes = 100  # 节点数

    def lock(self):
        while True:
            try:
                os.mkdir('.lock')
                return
            except Exception:
                pass

    def unlock(self):
        try:
            os.rmdir('.lock')
        except Exception:
            pass

    def check_json(self):
        self.lock()
        try:
            '''
            读txt，并检查格式，若正确，则返回True，否则返回False
            :return:
            '''
            with open(self.filename, 'r') as f:
                jvar = json.loads(f.read())
            self.unlock()
            while True:
                if len(jvar) != self.num_nodes:
                    # 检查节点个数
                    print('Number of nodes {0} is not {1}'.format(
                        len(jvar), self.num_nodes))
                    return False
                #
                for i in range(self.num_nodes):
                    # 检查每个节点内容
                    node = jvar[i]
                    #
                    if not node['malicious'] in (True, False):
                        print('"malicious" of node {0} is not bool'.format(i))
                        return False
                    #
                    if len(node['link_delay']) != self.num_nodes:
                        print('"link_delay" size {0} is not {1}'.format(
                            len(node['link_delay']), self.num_nodes))
                        return False
                return True
        finally:
            self.unlock()

    def run_check(self, interval):
        '''
        定时，每过interval秒执行一次指定函数
        :param interval:
        :return: True or False
        '''
        while True:
            try:
                # 休眠间隔中仍剩余的时间
                time_remaining = interval - time.time() % interval
                time.sleep(time_remaining)
                # 执行读文件操作并判断
                if self.check_json():
                    print('correct')
                else:
                    print('error')
            except Exception as e:
                print(e)


if __name__ == '__main__':
    chk = BcdChecker()
    chk.run_check(1)
