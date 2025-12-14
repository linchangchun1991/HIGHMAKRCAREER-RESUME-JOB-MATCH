import { NextRequest, NextResponse } from 'next/server';
import pdf from 'pdf-parse';
import mammoth from 'mammoth';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    let content = '';
    
    if (file.name.endsWith('.pdf')) {
      const data = await pdf(buffer);
      content = data.text;
    } else if (file.name.endsWith('.docx')) {
      const result = await mammoth.extractRawText({ buffer });
      content = result.value;
    } else if (file.name.endsWith('.doc')) {
      // 对于 .doc 文件，尝试提取文本
      content = buffer.toString('utf-8').replace(/[^\x20-\x7E\u4e00-\u9fff]/g, ' ');
    }

    return NextResponse.json({ 
      success: true, 
      content: content.trim(),
      filename: file.name 
    });
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json({ error: 'Upload failed' }, { status: 500 });
  }
}
