import argparse

from mongo_tool.insert import insertOne
from mongo_tool.delete import deleteMany
from mongo_tool.query import query
from mongo_tool.update import updateOne
# from common import hlog
from sys import argv


def main():
    parser = argparse.ArgumentParser(prog='mongo_tool',
                                     description='mongo工具',
                                     usage='%(prog)s [-i file] [-d filter] [-u filter json] [-q filter]')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-i',
                       '--insert',
                       help='将js文件内容写入数据库',
                       required=False,
                       nargs=1,
                       action='store',
                       metavar='file',
                       dest='insert')

    group.add_argument('-u',
                       '--update',
                       help='更改满足filter的数据',
                       required=False,
                       nargs=2,
                       action='store',
                       metavar=('filter', 'json'),
                       dest='update')

    group.add_argument('-q',
                       '--query',
                       help='查询满足filter的数据',
                       required=False,
                       nargs=1,
                       action='store',
                       metavar=('filter'),
                       dest='query')

    group.add_argument('-d',
                       '--delete',
                       help='删除所有满足条件的document',
                       required=False,
                       nargs=1,
                       action='store',
                       metavar=('filter'),
                       dest='delete')

    parser.add_argument('-v',
                        '--version',
                        help='显示版本信息',
                        action='version',
                        version='%(prog)s v1.0.0')

    args = parser.parse_args()

    if args.insert:  # 完成
        print('执行：insert')
        result = insertOne(argv[2])
        print('上传成功') if result else print('上传失败')
    elif args.delete:
        print('执行：delete')
        result = deleteMany(argv[2])
        if result.deleted_count == 0:
            print("没有符合条件的文档")
        else:
            print("已删除 %d 条符合条件的文档" % result.deleted_count)
    elif args.update:
        print('执行：update')
        result = updateOne(argv[2], argv[3])
        if result.matched_count == 0:
            print("没有符合条件的文档")
        else:
            print("更新成功，更新了 %d 条符合条件的文档" % result.matched_count)
    elif args.query:
        print('执行：query')
        result = query(argv[2])
        count = 0
        for x in result:
            print(x)
            count = count + 1
        if count == 0:
            print("没有符合条件的文档")
        else:
            print("查询成功，找到 %d 条符合条件的文档" % count)
    else:
        print('命令行参数错误，请查看使用说明')
        parser.print_help()
        exit(1)

    # client.run(directive=directive, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
