from PIL import Image

def UYVY_RAW2RGB_PIL(data, w, h):
    y=Image.frombytes('L',(w,h),data[1::2].copy())
    u=Image.frombytes('L',(w,h),data[0::4].reshape(w//2,h).copy().repeat(2, 0))
    v=Image.frombytes('L',(w,h),data[2::4].reshape(w//2,h).copy().repeat(2, 0))
    return Image.merge('YCbCr',(y,u,v))
