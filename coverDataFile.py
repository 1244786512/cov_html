# -*- coding: utf-8 -*-
import os, glob
from datetime import datetime


# author = wxf

class CoverDataFileMethod:

    def __init__(self, file):
        with open(file, encoding='utf-8') as covFile:
            self.contentCovData = covFile.read()
        self.contentCovTime = self.getCovFileTime(file)
        self.contentCov = self.contentCovData.replace("mode: count\n", "")
        self.goFileSign = ".go"
        self.isFileList = []
        self.contentDict = []
        self.rootFileName = ''
        self.funcLineOffset = 2   # 函数行偏移量
        self.covColorRange = {
            (0, 50): 'danger',
            (50, 90): 'warning',
        }

    # 覆盖率生成时间
    def getCovFileTime(self, file):
        try:
            last_timestamp = os.path.getmtime(file)
            last_datetime = datetime.fromtimestamp(last_timestamp)
            return last_datetime.strftime('%Y-%m-%d %H:%M:%S')
        except OSError as e:
            print(f"Error: {e}")
            return ''

    # 获取指定目录 指定后缀 文件个数
    def getCovDirectoryFile(self, directory):
        # 使用 glob 模块来匹配 .go 文件
        go_files = glob.glob(os.path.join(directory, '*.go'))
        # 返回 .go 文件的数量
        return len(go_files)

    # 根据覆盖率 返回 html class Color
    def getCovColor(self, covNumber):
        for (start, end), color in self.covColorRange.items():
            if start <= covNumber < end:
                return color
        return 'success'

    # 指定行读取函数结尾
    def funcEndLines(self, fileCodePath, startLine, endLine):
        with open(fileCodePath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for i in range(endLine - 1, startLine, -1):  # 索引从 func 上一行开始
                lineStr = lines[i - 1].strip()  # 文件索引
                if lineStr.endswith("}"):
                    return i
        return startLine

    # 补偿  函数嵌套读取不准确
    def funcOffsetLine(self, filePath, lineNum, funcDict):
        keyList = list(funcDict.keys())
        keyLength = len(keyList)
        for i in range(keyLength):
            endLine = funcDict[keyList[i]]["end"]
            if i + 1 == keyLength:
                startLine = lineNum
            else:
                startLine = funcDict[keyList[i + 1]]["start"]
            if startLine - endLine > self.funcLineOffset:
                endLine = self.funcEndLines(filePath, endLine, startLine)
                funcDict[keyList[i]]["end"] = endLine
                funcDict[keyList[i]]["line"] = endLine - funcDict[keyList[i]]["start"] + 1
        return funcDict

    # 有效总行数
    def getValidLines(self, funcDict):
        # 有效行数 所有 func 函数 总行数
        validCodeLines = 0
        for key in funcDict.keys():
            validCodeLines += funcDict[key]["line"]
        return validCodeLines

    # 获取文件行
    def getLineCount(self, fileCodePath):
        with open(fileCodePath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            funcRanges = {}
            currentFunc = None
            for idx, line in enumerate(lines):
                line = line.strip()
                if line.startswith("func ") and line.endswith("{"):
                    # todo
                    # func CreditAmount(c echo.Context)
                    currentFunc = line.split(" ")[1].split("(")[0]
                    if len(currentFunc) == 0:
                        # func (m *StandardClient) EntryApply(req entry.ClientEntryReqStruct) (standardvalueobject.StandardCommEncryptResult, error) {
                        currentFunc = line.split(" ")[3].split("(")[0]
                    start = idx + 1
                    funcRanges[currentFunc] = {"start": start}  # 行数从1开始计数
                elif currentFunc is not None:
                    if line.endswith("}"):
                        end = idx + 1
                        line = end - start + 1
                        funcRanges[currentFunc]["end"] = end  # 行数从1开始计数
                        funcRanges[currentFunc]["line"] = line
                        currentFunc = None
            # 去除末尾的空行
            while lines and lines[-1].strip() == "":
                lines.pop()
            totalLines = len(lines)

        #修正 函数结尾行数
        funcRanges = self.funcOffsetLine(fileCodePath, totalLines, funcRanges)
        validCodeLines = self.getValidLines(funcRanges)
        return totalLines, validCodeLines, funcRanges

    # 拆分 文件中的覆盖数据
    def getLineCovData(self, covLineCont):
        # 35.53,56.2 11 1
        covLineList = covLineCont.split(",")

        startLine = int(covLineList[0].split(".")[0])

        endLineData = covLineList[-1].split(".")
        endLine = int(endLineData[0])

        isCovList = covLineList[-1].split(' ')
        isCov = int(isCovList[-1])
        count = int(isCovList[-2])
        isCovLines = endLine - startLine + 1

        lineDict = {"startLine": startLine, "endLine": endLine, "count": count, "isCovList": isCovLines}
        if isCov == 0:
            isCovRow = False
        else:
            isCovRow = True
        return isCovRow, lineDict

    def getContentFileFormat(self, lineContent):

        parts = lineContent.split('/')

        # 递归终止条件：如果路径只有一部分（即当前目录或文件）
        if len(parts) == 1:
            return {'name': parts[0]}  # 文件没有子目录

        # 创建当前层级的目录结构
        current_part = parts[0]
        # 递归调用以创建子目录结构
        children_structure = self.getContentFileFormat('/'.join(parts[1:]))

        # 返回当前目录结构，可能包含子目录
        return {
            'name': current_part,
            'children': [children_structure]  # 子目录作为列表元素
        }

    def updateContentFileCovRowsList(self, filePath, projectData, isCovRow, covRowsDict):
        for item in projectData['children']:
            if item['isFolder']:
                self.updateContentFileCovRowsList(filePath, item, isCovRow, covRowsDict)
            elif item['filePath'] == filePath:
                if isCovRow:
                    item['isCovRowsList'].append(covRowsDict)
                else:
                    item['notCovRowsList'].append(covRowsDict)
                break

    def getContentBefore(self):
        # 最外层的目录
        self.rootFileName = self.contentCov.strip().split('\n')[0].split('/')[0]
        for path in self.contentCov.split('\n'):
            if path.strip():  # 跳过空行
                fileDataList = path.strip().split(":")
                filePath = fileDataList[0]
                fileLinePath = filePath.replace("{0}/".format(self.rootFileName), "")
                fileCovData = fileDataList[-1]
                if filePath in self.isFileList:
                    # 处理过  更新 isCovRowsList notCovRowsList
                    if self.goFileSign in filePath:
                        # 文件
                        isCovRow, lineDict = self.getLineCovData(fileCovData)
                        self.updateContentFileCovRowsList(fileLinePath, self.contentDict[0], isCovRow, lineDict)
                    else:
                        print('已处理过，非文件数据')
                else:
                    # 第一次处理

                    # 将 filePath 加入到 self.isFileList 不处理递归
                    self.isFileList.append(filePath)
                    currentNode = self.contentDict
                    directories = filePath.strip("/").split("/")

                    for index,directory in enumerate(directories):
                        # 检查当前目录是否已经存在于当前节点的子目录中
                        existing_directory = next((d for d in currentNode if d["name"] == directory), None)
                        if existing_directory:
                            currentNode = existing_directory["children"]
                        else:
                            # 如果当前目录不存在，则创建一个新的节点，并将其添加到当前节点的子目录中
                            itemList = directories[0:index]
                            parentDir = '/' + '/'.join(itemList)
                            newDirectory = {"name": directory, "parentDir": parentDir, "children": []}
                            if self.goFileSign in directory:
                                # 文件
                                newDirectory['isFolder'] = False
                                newDirectory['filePath'] = fileLinePath
                                newDirectory['icon'] = 'static/icons/file-code.svg'
                                newDirectory['totalFile'] = 1
                                # 处理行数问题
                                isCovRowsList = []  # 已覆盖行数
                                notCovRowsList = []  # 未覆盖行数
                                isCovRow, lineDict = self.getLineCovData(fileCovData)
                                if isCovRow:
                                    isCovRowsList.append(lineDict)
                                else:
                                    notCovRowsList.append(lineDict)
                                newDirectory['isCovRowsList'] = isCovRowsList
                                newDirectory['notCovRowsList'] = notCovRowsList

                                # 处理文件总行数&有效行数
                                codeLines, codeLinesValid, funcRanges = self.getLineCount(fileLinePath)
                                newDirectory['codeLines'] = codeLines
                                newDirectory['codeLinesValid'] = codeLinesValid
                                newDirectory['codeFuncList'] = funcRanges
                            else:
                                # 文件夹
                                newDirectory['isFolder'] = True
                                newDirectory['icon'] = 'static/icons/file-directory.svg'
                                newDirectory['totalFile'] = 0
                            currentNode.append(newDirectory)
                            currentNode = newDirectory["children"]

        return self.contentDict[0], self.rootFileName, self.contentCovTime

    # 计算 覆盖总行数
    def getLineCompute(self, intervals):
        intervals.sort()  # 按照区间的起点进行排序
        totalLength = 0
        prevEnd = None

        for start, end in intervals:
            if prevEnd is None or start > prevEnd:
                # 如果当前区间与前一个区间不重叠，或者是第一个区间，则直接加上当前区间的长度（包括起点和终点）
                totalLength += end - start + 1
                prevEnd = end
            elif end > prevEnd:
                # 如果当前区间与前一个区间重叠，但是超出了前一个区间的结束点，则只加上重叠部分的长度（包括终点）
                totalLength += end - prevEnd
                prevEnd = end

        return totalLength

    # 计算 函数覆盖
    def getIsFuncCov(self, funcList, lineComputeList):
        start1, end1 = funcList
        for sublist in lineComputeList:
            start2, end2 = sublist
            if start1 <= end2 and start2 <= end1:
                return True
        return False

    def getIsCovRowsList(self, node):
        if 'isCovRowsList' in node:
            lineComputeList = []
            for item in node['isCovRowsList']:
                lineComputeList.append([item['startLine'], item['endLine']])
            isCovLines = self.getLineCompute(lineComputeList)
            node['isCovLines'] = isCovLines
            try:
                node['isCodeCovLines'] = round(isCovLines/node['codeLinesValid'] * 100, 2)
            except ZeroDivisionError as e:
                node['isCodeCovLines'] = 0.0
            node['codeFunc'] = len(node['codeFuncList'])
            isCovFunc = 0
            for itemKeys in node['codeFuncList'].keys():
                item = node['codeFuncList'][itemKeys]
                isCovFuncSign = self.getIsFuncCov([item['start'], item['end']], lineComputeList)
                if isCovFuncSign:
                    item['isCov'] = True
                    isCovFunc += 1
                else:
                    item['isCov'] = False
            node['isCovFunc'] = isCovFunc
            try:
                node['isCodeCovFunc'] = round(isCovFunc/node['codeFunc'] * 100, 2)
            except ZeroDivisionError as e:
                node['isCodeCovFunc'] = 0.0
        if 'children' in node:
            for child in node['children']:
                self.getIsCovRowsList(child)

        return node  # 返回处理后的节点

    def updateParentIsCovLines(self, node):
        if not node:
            return 0

        # 行
        totalIsCovLines = node.get("isCovLines", 0)
        totalCodeLinesValid = node.get("codeLinesValid", 0)
        totalCodeLines = node.get("codeLines", 0)
        # 函数
        totalCodeFunc = node.get("codeFunc", 0)
        totalIsCovFunc = node.get("isCovFunc", 0)
        # 文件数量
        totalFile = node.get("totalFile", 0)

        children = node.get("children", [])
        for child in children:
            resDict = self.updateParentIsCovLines(child)
            totalIsCovLines += resDict[0]
            totalCodeLinesValid += resDict[1]
            totalCodeLines += resDict[2]
            totalCodeFunc += resDict[3]
            totalIsCovFunc += resDict[4]
            totalFile += resDict[5]

        # 行
        try:
            isCodeCovLines = round(totalIsCovLines / totalCodeLinesValid * 100, 2)
        except ZeroDivisionError as e:
            isCodeCovLines = 0.0
        node["isCovLines"] = totalIsCovLines
        node["codeLinesValid"] = totalCodeLinesValid
        node["codeLines"] = totalCodeLines
        node["isCodeCovLines"] = isCodeCovLines
        node["colorCodeClass"] = self.getCovColor(isCodeCovLines)

        # 函数
        try:
            isCodeCovFunc = round(totalIsCovFunc / totalCodeFunc * 100, 2)
        except ZeroDivisionError as e:
            isCodeCovFunc = 0.0
        node["codeFunc"] = totalCodeFunc
        node["isCovFunc"] = totalIsCovFunc
        node["isCodeCovFunc"] = isCodeCovFunc
        node["colorFuncClass"] = self.getCovColor(isCodeCovFunc)

        # 文件
        node["totalFile"] = totalFile
        return totalIsCovLines, totalCodeLinesValid, totalCodeLines, totalCodeFunc, totalIsCovFunc, totalFile, node
