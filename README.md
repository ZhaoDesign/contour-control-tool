# Nano Banana 轮廓控制图工具

这是一个轻量工具，用来把真人参考图处理成“线条控制图”，方便在 Nano Banana 里控制人物姿势、场景结构和构图。

核心目标：

- 不复制原图人物身份
- 弱化原脸五官
- 保留人物姿势和场景结构
- 导出 PNG 控制图
- 免费部署到 GitHub Pages

## 在线网页版本

直接打开：

```text
index.html
```

功能：

- 上传参考图
- 转灰度
- 模糊降噪
- Sobel 轮廓提取
- 调整轮廓强度
- 调整浅线保留
- 调整线条加粗
- 弱化脸部区域
- 下载 PNG 控制图
- 复制配套 Nano Banana 提示词

所有处理都在浏览器本地完成，图片不会上传到服务器。

## 免费部署到 GitHub Pages

1. 新建一个 GitHub 仓库。
2. 把这个文件夹里的内容上传到仓库。
3. 进入仓库设置：`Settings` -> `Pages`。
4. `Build and deployment` 选择：

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

5. 保存后等待 GitHub Pages 自动生成网址。

之后其他同学打开这个网址就能直接使用。

## 本地脚本版本

脚本位置：

```text
scripts/contour_control.py
```

第一次使用前安装 Pillow：

```bash
python3 -m pip install pillow
```

示例：

```bash
python3 scripts/contour_control.py input.png -o output-control.png
```

推荐参数：

```bash
python3 scripts/contour_control.py input.png -o output-control.png \
  --blur 1.4 \
  --threshold 42 \
  --softness 56 \
  --thicken 1 \
  --face-center 50,23 \
  --face-size 24,17
```

如果不想弱化脸部：

```bash
python3 scripts/contour_control.py input.png -o output-control.png --no-face-mute
```

## 参数说明

| 参数 | 作用 |
| --- | --- |
| `--blur` | 模糊降噪，数值越大，皮肤纹理和背景噪点越少 |
| `--threshold` | 轮廓强度，数值越低，线条越多 |
| `--softness` | 浅线保留，数值越高，灰色辅助线越多 |
| `--thicken` | 线条加粗，适合让模型更容易识别姿势 |
| `--face-center` | 脸部弱化椭圆中心，格式是 `x,y` 百分比 |
| `--face-size` | 脸部弱化椭圆大小，格式是 `宽,高` 百分比 |

## 推荐 Nano Banana 提示词

```text
参考图只作为线条控制图使用，只控制人物姿势、身体轮廓、坐姿、手部位置、镜头角度、场景结构和空间关系。不要参考线条图中的脸部五官，不要复制原人物头部；人物头部、脸型、五官和发型以文字提示或另一张人物参考图为准。控制图只锁定姿势和场景，不锁定身份。不要生成畸形头部，不要扭曲五官，不要把脸做成原图人物。
```

## 使用建议

- 如果头部容易坏，把脸部弱化椭圆调大一点。
- 如果场景消失，把轮廓强度调低一点，让背景线条更多。
- 如果画面太乱，把模糊降噪调高一点，或者把浅线保留调低。
- 如果姿势不稳定，把线条加粗调到 `2`。

## 技术说明

网页版本使用 Canvas 在浏览器本地处理图像。

本地脚本使用 Python 和 Pillow。

处理流程：

```text
上传图片
-> 转灰度
-> 模糊降噪
-> Sobel 边缘提取
-> 黑白/浅灰轮廓输出
-> 可选脸部弱化
-> 导出 PNG
```
