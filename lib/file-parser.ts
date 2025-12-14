import mammoth from "mammoth"

/**
 * 解析 PDF 文件
 */
export async function parsePDF(buffer: Buffer): Promise<string> {
  try {
    // 动态导入 pdf-parse（CommonJS 模块）
    const pdfParse = (await import("pdf-parse")).default || await import("pdf-parse")
    const parseFunction = typeof pdfParse === "function" ? pdfParse : (pdfParse as any).default || pdfParse
    const data = await parseFunction(buffer)
    return data.text
  } catch (error) {
    throw new Error(`PDF 解析失败: ${error instanceof Error ? error.message : "未知错误"}`)
  }
}

/**
 * 解析 Word 文件（.docx）
 */
export async function parseWord(buffer: Buffer): Promise<string> {
  try {
    const result = await mammoth.extractRawText({ buffer })
    return result.value
  } catch (error) {
    throw new Error(`Word 解析失败: ${error instanceof Error ? error.message : "未知错误"}`)
  }
}

/**
 * 根据文件类型解析文件
 */
export async function parseFile(file: File): Promise<string> {
  const arrayBuffer = await file.arrayBuffer()
  const buffer = Buffer.from(arrayBuffer)

  if (file.type === "application/pdf" || file.name.endsWith(".pdf")) {
    return parsePDF(buffer)
  } else if (
    file.type.includes("word") ||
    file.name.endsWith(".docx") ||
    file.name.endsWith(".doc")
  ) {
    return parseWord(buffer)
  } else {
    throw new Error("不支持的文件格式，请上传 PDF 或 Word 文档")
  }
}
