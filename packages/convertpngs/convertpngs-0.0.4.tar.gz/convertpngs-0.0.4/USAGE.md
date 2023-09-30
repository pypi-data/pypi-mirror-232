### USAGE

#### Convert pngs to gif
If you want to convert the png files to gif, you can use the function `to_gif` in the module `convert_pngs`. The function has three parameters, the first one is the input folder path, the second one is the output file name, and the third one is the duration of each frame. The default value of the third parameter is 100, which means 100 milliseconds. The function will return the path of the output file.

```python
# 導入套件
from convertpngs import convert_pngs as cp

# 指定輸入資料夾和輸出GIF文件的名稱
input_folder = 'hotspot_TPP'  # 替換PNG檔案所在的資料夾路徑
output_file = 'output.gif'  # 替換為輸出的GIF檔案名稱
cp.to_gif(input_folder, output_file, duration=100, loop=0) # 每一張的顯示時間，100就是100毫秒
```

#### Convert pngs to mp4
If you want to convert the png files to mp4, you can use the function `to_mp4` in the module `convert_pngs`. The function has three parameters, the first one is the input folder path, the second one is the output file name, and the third one is the fps of the video. The default value of the third parameter is 10, which means 10 frames per second. The function will return the path of the output file.

```python
# 導入套件
from convertpngs import convert_pngs as cp

# 指定輸入資料夾和輸出MP4文件的名稱
input_folder = 'hotspot'  # 替換為PNG檔案所在的資料夾路徑
output_file = 'output.mp4'  # 替換為輸出的MP4文件名稱
cp.to_mp4(input_folder, output_file, fps=30)  # 這裡的fps是幀率，可以根據需要調整
```

Let's all, enjoy the beauty of simplification of this module.

---