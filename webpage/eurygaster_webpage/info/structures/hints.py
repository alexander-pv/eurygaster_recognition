from collections import namedtuple

BasicMsg = namedtuple('BasicMsg',
                      'ASK_IMAGE FILTER_DESCR CLASSIFIER_DESCR INCORRECT_INPUT EMPTY_INPUT WAS_FILTERED RECOGNIZED_AS')

EngMsg = BasicMsg("Please, upload an image file",
                  "Confidence that this is the picture of Eurygaster spp.:",
                  "Confidence distribution of species if Eurygaster is in the picture:",
                  "The input contains undefined data. Perhaps it is a masked file of another data type.",
                  "No image input",
                  "No Eurygaster found in the image",
                  "Found %s with confidence %.3f",
                  )
RuMsg = BasicMsg("Пожалуйста, загрузите фотографию",
                 "Вероятность, что на фотографии Eurygaster spp.:",
                 "Распределение вероятностей принадлежности к каждому из видов Eurygaster:",
                 "На вход поданы некорректные данные.",
                 "Изображение не загружено",
                 "На изображении не найдено Eurygaster",
                 "Обнаружен %s с уверенностью %.3f",
                 )
CnMsg = BasicMsg("請上傳圖像文件",
                 "確信這是 Eurygaster spp. 的照片：",
                 "如果圖中有 Eurygaster，則物種的置信度分佈：",
                 "輸入包含未定義的數據。 也許它是另一種數據類型的屏蔽文件",
                 "無圖像輸入",
                 "圖像中未發現 Eurygaster",
                 "有信心找到 %s %.3f",
                 )
DefaultMsg = EngMsg
HINT_MESSAGES = {
    'en': EngMsg,
    'ru': RuMsg,
    'cn': CnMsg
}
