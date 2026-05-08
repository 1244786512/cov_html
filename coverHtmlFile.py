# -*- coding: utf-8 -*-
import os, shutil, math
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound

# author = wxf


class CoverHtmlFileMethod:

    def __init__(self, reportDirectory="report"):
        self.coverDirectory = reportDirectory
        self.coverFileStatic = "static"
        self.coverSymbol = "../"
        self.covRenderTemplate = "reportModelBase.html"
        self.currentPath = os.path.abspath(__file__)
        self.parentPath = os.path.dirname(self.currentPath )

    # 删除文件夹
    def covFileDelete(self, folderPath):
        try:
            if os.path.exists(folderPath):
                shutil.rmtree(folderPath)
                print(f"文件夹 {folderPath} 已成功删除")
            else:
                print(f"文件夹 {folderPath} 不存在")
        except Exception as e:
            print(f"删除文件夹 {folderPath} 出错：{e}")

    # 创建文件夹
    def covFileCreate(self, folderPath):
        try:
            os.mkdir(folderPath)
            print(f"文件夹 {folderPath} 已成功创建")
        except Exception as e:
            print(f"操作文件夹 {folderPath} 出错：{e}")

    # 复制文件
    def covFileCopy(self, sourceItem, destination):
        try:
            # 如果目标文件夹存在，则先删除
            if os.path.exists(destination):
                self.covFileDelete(destination)

            # 复制文件夹及其内容
            shutil.copytree(sourceItem, destination)
            print(f"文件夹 {sourceItem} 已成功复制到 {destination}")
        except Exception as e:
            print(f"复制文件夹出错：{e}, 重试中")
            sourceItem = self.parentPath + '/static'
            self.covFileCopy(sourceItem, destination)

    # 新建报告文件夹
    def covCreateReportDirectory(self, sourceStaticFile, fileName):
        folderPath = os.path.join(os.getcwd(), fileName + '/' + sourceStaticFile)
        # 复制
        sourceStatic = os.path.join(os.getcwd(), sourceStaticFile)
        self.covFileCopy(sourceStatic, folderPath)

    # 读代码文件内容
    def covRenderCodeContent(self, codeFile):
        with open(codeFile, "r", encoding='utf-8') as f:
            contentData = f.readlines()
        return contentData

    # 过滤渲染后模板 中的 空行
    def covRenderEmptyLines(self, renderString):
        # 将字符串按行分割
        lines = renderString.splitlines()
        # 过滤掉空行
        filtered_lines = [line for line in lines if line.strip() != ""]
        # 保留原始格式
        result = "\n".join(filtered_lines)
        return result

    # 渲染模板
    def covRenderTemplateHtml(self, templateFilePath, templateFileData):
        try:
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template(self.covRenderTemplate)
        except TemplateNotFound:
            env = Environment(loader=FileSystemLoader(self.parentPath + "/templates", 'utf-8'))
            template = env.get_template(self.covRenderTemplate)

        # 渲染基础模板并填充各个部分的内容
        base_template = template.render(templateFileData)

        # 导出结果
        with open(self.coverDirectory + templateFilePath, "w", encoding='utf-8') as f:
            f.write(self.covRenderEmptyLines(base_template))

        # print("Template rendering and export complete.")

    # 遍历数据
    def covHtmlFile(self, projectData, rootName, covTime):
        if isinstance(projectData, dict):
            # 公共数据处理
            # 数据组装
            isFolder = projectData['isFolder']
            totalFile = projectData['totalFile']
            bodyList = []

            # 行数据
            codeLinesValid = projectData['codeLinesValid']
            isCovLines = projectData['isCovLines']
            notCovLines = codeLinesValid - isCovLines
            isCodeCovLines = projectData['isCodeCovLines']
            totalLine = projectData['codeLines']
            try:
                summaryLinesCov = math.ceil(isCodeCovLines)
            except ZeroDivisionError as e:
                summaryLinesCov = 0

            # 方法数据
            codeFunc = projectData['codeFunc']
            isCovFunc = projectData['isCovFunc']
            notCovFunc = codeFunc - isCovFunc
            isCodeCovFunc = projectData['isCodeCovFunc']
            totalMethod = codeFunc
            try:
                summaryMethodCov = math.ceil(isCodeCovFunc)
            except ZeroDivisionError as e:
                summaryMethodCov = 0

            totalBody = {
                "name": "Total",
                "codeLinesValid": codeLinesValid,
                "isCovLines": isCovLines,
                "isCodeCovLines": isCodeCovLines,
                "codeFunc": codeFunc,
                "isCovFunc": isCovFunc,
                "isCodeCovFunc": projectData['isCodeCovFunc'],
                "colorCodeClass": projectData['colorCodeClass'],
                "colorFuncClass": projectData['colorFuncClass'],
                "icon": "",
                "isFolder": isFolder
            }
            bodyList.append(totalBody)

            projectDataLen = len(projectData['children'])
            # 判断 是否有子目录
            if projectDataLen > 0:
                # 循环子目录
                for child in projectData['children']:
                    childBody = {
                        "name": child['name'],
                        "codeLinesValid": child['codeLinesValid'],
                        "isCovLines": child['isCovLines'],
                        "isCodeCovLines": child['isCodeCovLines'],
                        "codeFunc": child['codeFunc'],
                        "isCovFunc": child['isCovFunc'],
                        "isCodeCovFunc": child['isCodeCovFunc'],
                        "colorCodeClass": child['colorCodeClass'],
                        "colorFuncClass": child['colorFuncClass'],
                        "icon": child['icon'],
                        "isFolder": child['isFolder']
                    }
                    bodyList.append(childBody)

            templateFileData = {
                "html": {
                    "isFolder": isFolder,
                    "summaryContainer": {
                        "totalFile": totalFile,
                        "codeLinesValid": codeLinesValid,
                        "isCovLines": isCovLines,
                        "notCovLines": notCovLines,
                        "summaryLinesCov": summaryLinesCov,
                        "totalLine": totalLine,
                        "codeFunc": codeFunc,
                        "isCovFunc": isCovFunc,
                        "notCovFunc": notCovFunc,
                        "summaryMethodCov": summaryMethodCov,
                        "totalMethod": totalMethod
                    }
                },
                "body": bodyList,
                "footer": covTime
            }

            parentDirPath = projectData['parentDir']
            if parentDirPath == '/':
                parentDirectory = ''
                pathHeader = '/' + projectData['name']
            else:
                # 特殊处理文件夹
                parentDirectory = parentDirPath + '/' + projectData['name']
                fileName = '/' + rootName
                if parentDirectory.startswith(fileName, 0, len(fileName)):
                    parentDirectory = parentDirectory[len(fileName):]
                pathHeader = projectData['parentDir'] + '/' + projectData['name']

            # 1.检查目录
            # 2.创建目录
            # 3.写文件
            if isFolder:
                if os.path.exists(self.coverDirectory + parentDirectory):
                    print(self.coverDirectory + parentDirectory, '目录存在跳过创建')
                else:
                    os.mkdir(self.coverDirectory + parentDirectory)

                templateFilePath = parentDirectory + '/index.html'
                templateFileData['header'] = {
                        "path": pathHeader
                    }
                # print(f"Folder: {projectData['name']}", templateFilePath, templateFileData)
                self.covRenderTemplateHtml(templateFilePath, templateFileData)
            else:
                templateFileData['code'] = {
                    "codeContent": self.covRenderCodeContent(projectData['filePath']),
                    "isCovRowsList": projectData['isCovRowsList']
                }
                templateFilePath = parentDirectory + '.html'
                pathHeader = projectData['parentDir'] + '/' + projectData['name']
                templateFileData['header'] = {
                        "path": pathHeader
                    }
                # print(f"File: {projectData['name']}", templateFilePath, templateFileData)
                self.covRenderTemplateHtml(templateFilePath, templateFileData)

            if projectDataLen > 0:
                for child in projectData['children']:
                    self.covHtmlFile(child, rootName, covTime)

        elif isinstance(projectData, list):
            # 遍历列表中的每个元素
            for item in projectData['children']:
                self.covHtmlFile(item, rootName, covTime)
        else:
            print("Invalid projectData Format")

    def covHtmlRun(self, projectData, rootName, covTime):
        # 先删除
        # 创建
        # 复制
        # 生成
        self.covFileDelete(self.coverDirectory)
        self.covCreateReportDirectory(self.coverFileStatic, self.coverDirectory)
        self.covHtmlFile(projectData, rootName, covTime)
