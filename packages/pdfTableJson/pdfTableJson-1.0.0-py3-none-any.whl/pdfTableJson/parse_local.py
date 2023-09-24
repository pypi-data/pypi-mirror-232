import converter  # package # utf-8
import json

# PDF 파일 경로
path = "C:/Users/aria1/OneDrive/바탕 화면/프로젝트/pdf처리/자료2/004.pdf"

# 기본
exclude_list = ['열\n', '열 \n', '람\n', '람 \n', '용\n', '용 \n', '열 람\n', '열 람 \n', '람 용\n', '람 용 \n', '열 람 용\n', '열 람 용 \n', '열람\n', '열람 \n', '람용\n', '람용 \n', '열람용\n', '열람용 \n']
# 추가
exclude_list += ['용 ']
result = converter.main(path, exclude_list)

# print("===================================================================")

print(result)