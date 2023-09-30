# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 02:18:09 2023

@author: simon
"""

import os
from PIL import Image
import cv2

def to_gif(input_folder, output_file, duration=100, loop=0):
    '''
    將PNG檔案轉換為GIF動畫
    輸入參數：
    input_folder：PNG檔案所在的資料夾路徑
    output_file：輸出的GIF檔案名稱
    duration：每一張的顯示時間，單位為毫秒
    loop：迴圈次數，0為無限迴圈    
    '''
    # 檢查輸入資料夾是否存在
    if not os.path.exists(input_folder):
        print(f"資料夾 {input_folder} 不存在")
        return

    # 獲取資料夾中的所有PNG檔案，並按文件名排序
    png_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.png')])

    # 檢查是否存在PNG檔案
    if not png_files:
        print(f"資料夾 {input_folder} 中沒有PNG檔案")
        return

    # 打開PNG檔案並添加到列表中
    images = []
    for i, png_file in enumerate(png_files):
        img = Image.open(png_file)
        if i == 0:
            width, height = img.size
        img = img.resize((width, height), Image.ANTIALIAS)
        images.append(img)

    # 建立GIF文件
    images[0].save(output_file, save_all=True, append_images=images[1:], duration=duration, loop=loop)
    print(f"[HINT] GIF {output_file} 創建完成")










# =============================================================================

def to_mp4(input_folder, output_file, fps=10): # fps為幀率
    '''
    將PNG檔案轉換為MP4動畫
    輸入參數：
    input_folder：PNG檔案所在的資料夾路徑
    output_file：輸出的MP4檔案名稱
    fps：幀率，每秒播放的幀數
    '''
    # 檢查輸入資料夾是否存在
    if not os.path.exists(input_folder):
        print(f"資料夾 {input_folder} 不存在")
        return

    # 獲取資料夾中的所有PNG檔案，並按文件名排序
    png_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.png')])

    # 檢查是否存在PNG檔案
    if not png_files:
        print(f"資料夾 {input_folder} 中沒有PNG檔案")
        return

    # 獲取第一個PNG檔案的寬度和高度
    img = cv2.imread(png_files[0])
    height, width, layers = img.shape

    # 設置影片編、解碼器和寫入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    # 逐一讀取PNG檔案並寫入影片
    for png_file in png_files:
        img = cv2.imread(png_file)
        out.write(img)

    # 釋放寫入器
    out.release()
    print(f"[HINT] 動畫 {output_file} 創建完成")

