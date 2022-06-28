from openpyxl import Workbook
from openpyxl import styles

class RollListBookGenerator:
    def __init__(self, rollList, regEventId):
        self.rollList = rollList
        self.regEvent = regEventId
    def generate_workbook(self):
        workbook = Workbook()
        workbook.remove(workbook.active)

        self.generate_roll_sheet(workbook=workbook)
        return workbook
    
    def generate_roll_sheet(self, workbook):
        file = str(self.regEvent)
        file = file.replace(':', '-')
        worksheet = workbook.create_sheet(title = "{filename}".format(filename=file))
        headers = ['id', 'RegEventId', 'RegNo', 'Cycle', 'Section']
        row_num = 1
        for col_num, column_title in enumerate(headers,1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.font = styles.Font(bold = True)
            cell.value = column_title
        
        for roll in self.rollList:
            row_num+=1
            row_data = [
                roll.id,
                roll.RegEventId_id,
                roll.student.RegNo,
                roll.Cycle,
                roll.Section
            ]
            for col_num, cell_value in enumerate(row_data,1):
                cell = worksheet.cell(row=row_num, column=col_num)
                cell.value = cell_value