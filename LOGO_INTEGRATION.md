# 海马职加 LOGO 集成说明

## ✅ 已完成的工作

### 1. LOGO 文件位置
- **路径**: `public/assets/highmark-logo.png`
- **格式**: PNG（透明背景）
- **尺寸**: 原始尺寸（已优化）

### 2. 已更新的页面

#### 登录页面 (`app/page.tsx`)
- ✅ 替换文字 "HIGHMARK" 为 LOGO 图片
- ✅ 居中显示，尺寸：240x80px
- ✅ 响应式设计，移动端自适应

#### 仪表盘布局 (`app/dashboard/layout.tsx`)
- ✅ 侧边栏顶部显示 LOGO
- ✅ 尺寸：160x50px
- ✅ 适配侧边栏宽度

#### 教练端页面 (`app/dashboard/coach/page.tsx`)
- ✅ 左上角显示 LOGO
- ✅ 尺寸：180x60px（桌面端），自适应（移动端）
- ✅ 固定定位，不随页面滚动

## 🎨 设计特点

### 响应式设计
- **桌面端**: 较大尺寸，清晰可见
- **移动端**: 自动缩小，保持比例
- **平板端**: 中等尺寸，平衡显示

### 位置和样式
1. **登录页**: 居中显示，突出品牌
2. **侧边栏**: 顶部显示，导航标识
3. **教练端**: 左上角固定，品牌展示

### 图片优化
- 使用 Next.js Image 组件
- 自动优化和懒加载
- 支持 WebP 和 AVIF 格式
- 响应式尺寸调整

## 🔧 技术实现

### Next.js Image 组件
```tsx
import Image from "next/image"

<Image
  src="/assets/highmark-logo.png"
  alt="海马职加 High Mark Career"
  width={180}
  height={60}
  className="h-auto w-auto max-w-[180px] lg:max-w-[220px]"
  priority
/>
```

### 配置说明
- `priority`: 优先加载（首屏显示）
- `width/height`: 设置尺寸（用于优化）
- `className`: 响应式样式控制
- `alt`: 无障碍访问文本

## 📱 响应式断点

### 登录页面
- **桌面端**: 240px 宽度
- **移动端**: 自动缩小

### 侧边栏
- **所有尺寸**: 160px 宽度

### 教练端页面
- **桌面端**: 180-220px 宽度
- **移动端**: 自动缩小

## 🎯 使用建议

### 如需更换 LOGO
1. 替换 `public/assets/highmark-logo.png` 文件
2. 保持文件名一致
3. 建议使用 PNG 格式（支持透明背景）
4. 建议尺寸比例：约 3:1（宽:高）

### 如需调整尺寸
在各页面的 Image 组件中修改：
- `width`: 宽度（像素）
- `height`: 高度（像素）
- `className`: CSS 类名（响应式控制）

## 📝 注意事项

1. **文件路径**: 使用 `/assets/highmark-logo.png`（public 目录下的文件）
2. **图片格式**: 建议使用 PNG（支持透明背景）或 SVG（矢量图）
3. **文件大小**: 建议控制在 200KB 以内
4. **加载性能**: 使用 `priority` 属性确保首屏快速加载

## 🚀 后续优化建议

1. **SVG 格式**: 考虑使用 SVG 格式以获得更好的缩放效果
2. **暗色模式**: 如需支持暗色模式，可准备深色版本 LOGO
3. **Favicon**: 可基于 LOGO 创建网站图标
4. **加载动画**: 可添加 LOGO 加载动画效果
