import os
import time
import sys
import subprocess
from PIL import Image

# 版本号
VERSION = "1.0.6"

# 检查并安装 Pillow
def install_pillow():
    try:
        import PIL
        print("Pillow 已安装，跳过安装过程。")
    except ImportError:
        print("Pillow 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
        print("Pillow 安装完成。")

# 文件名最大长度
MAX_FILENAME_LENGTH = 8

def truncate_filename(filename):
    """截取文件名，确保长度不会超过 MAX_FILENAME_LENGTH"""
    name, ext = os.path.splitext(filename)
    if len(name) > MAX_FILENAME_LENGTH:
        name = name[:MAX_FILENAME_LENGTH] + '...'
    return name + ext

def get_unique_filename(output_dir, base_name):
    """生成唯一的文件名，避免覆盖"""
    file_name = base_name
    counter = 1
    while os.path.exists(os.path.join(output_dir, f"{file_name}.webp")):
        file_name = f"{base_name.split('.')[0]}_{counter}"
        counter += 1
    return file_name

def convert_to_webp(input_path, output_path, quality_level):
    """将图片转换为 WebP 格式"""
    if quality_level < 1 or quality_level > 5:
        print("质量等级必须在 1 到 5 之间。")
        return False
    
    # 将质量等级转换为适应 WebP 的 10, 30, 50, 70, 90 的质量值
    webp_quality = (quality_level - 1) * 20 + 10  # 转换为 WebP 格式的质量值（10, 30, 50, 70, 90）

    try:
        with Image.open(input_path) as img:
            # 转换为 WebP 格式并保存
            img.save(output_path, format="WEBP", quality=webp_quality)
            print(f"[{input_path}] 转换完成，保存为 {output_path}，质量等级：{quality_level}，WebP质量值：{webp_quality}")
            return True  # 成功转换，返回 True
    except Exception as e:
        print(f"转换失败: {e}")
        return False  # 转换失败，返回 False

def verify_conversion(output_path):
    """检查转换后的 WebP 文件是否有效"""
    try:
        with Image.open(output_path) as img:
            img.verify()  # 验证图像文件
        # 验证文件大小是否合理
        if os.path.getsize(output_path) > 0:
            print(f"文件验证成功: {output_path}")
            return True
        else:
            print(f"文件大小为 0，验证失败: {output_path}")
            return False
    except Exception as e:
        print(f"文件验证失败: {e}")
        return False

def display_animation():
    """创建旋转动画"""
    animation = ['|', '/', '-', '\\']
    idx = 0
    while True:
        sys.stdout.write(f'\r{animation[idx]} 正在转换图片...')
        sys.stdout.flush()
        idx = (idx + 1) % 4
        time.sleep(0.1)  # 动画每0.1秒更新一次

def search_and_convert_images_in_current_dir(quality_level):
    """遍历目录并转换图片"""
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # 遍历目录并计数
    total_files = 0
    processed_files = 0
    failed_files = 0  # 记录失败的文件数
    failed_files_list = []  # 记录失败的文件详细信息
    
    for root, dirs, files in os.walk(script_dir):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp')):
                total_files += 1

    print(f"找到 {total_files} 张图片文件，开始转换...")

    # 启动动画
    import threading
    animation_thread = threading.Thread(target=display_animation)
    animation_thread.daemon = True
    animation_thread.start()

    # 进行转换
    for root, dirs, files in os.walk(script_dir):
        for file in files:
            if file.lower().endswith(('jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp')):
                input_path = os.path.join(root, file)
                truncated_name = truncate_filename(file)
                output_base_name = f"new_{truncated_name.split('.')[0]}"
                unique_output_name = get_unique_filename(root, output_base_name)
                output_path = os.path.join(root, f"{unique_output_name}.webp")
                
                # 转换
                if convert_to_webp(input_path, output_path, quality_level):
                    # 验证转换后的图片
                    if not verify_conversion(output_path):
                        print(f"转换后的文件无效: {output_path}")
                        failed_files += 1
                        failed_files_list.append(f"无效文件: {output_path}")
                else:
                    failed_files += 1
                    failed_files_list.append(f"转换失败的文件: {input_path}")
                
                # 删除原图片文件
                try:
                    os.remove(input_path)
                    print(f"已删除原图片: {input_path}")
                except Exception as e:
                    print(f"删除原图片失败: {e}")
                
                # 更新已处理的文件计数，并显示进度
                processed_files += 1
                print(f"进度: {processed_files}/{total_files} 处理完成")

    # 停止动画并输出结果
    print("\r\033[1;32m转换完成，所有文件已处理。\033[0m")  # 使用绿色加粗文本显示
    if failed_files > 0:
        print(f"有 {failed_files} 张图片转换失败，请检查错误信息：")
        for error in failed_files_list:
            print(error)

    sys.stdout.flush()

    # 自动退出程序
    print("程序处理完成，自动退出...")
    sys.exit()

if __name__ == "__main__":
    # 显示版本信息和版权信息
    print(f"程序版本：{VERSION}")
    print("版权信息：")
    print("OKSGO 版权所有")
    print("更多信息，请访问：https://oksgo.com/")

    # 安装 Pillow（如果未安装）
    install_pillow()

    # 显示程序说明
    print("\n欢迎使用图片转换程序！")
    print("该程序支持将以下格式的图片转换为 WebP 格式：")
    print("JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP")
    print("程序将自动使用最低质量进行转换，质量等级为 1。")
    
    # 设置固定质量等级为 1
    quality_level = 1

    # 开始转换
    search_and_convert_images_in_current_dir(quality_level)
