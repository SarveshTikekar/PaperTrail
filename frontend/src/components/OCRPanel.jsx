import { useState } from 'react'
import axios from 'axios'

export default function OCRPanel() {
  const [file, setFile] = useState(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!file) return setError('Please select an image file')

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('image', file)

      const response = await axios.post('http://127.0.0.1:8000/api/ocr/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setText(response.data.text || '')
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'OCR failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto p-4 bg-white shadow-lg rounded-lg">
      <h2 className="text-2xl font-semibold mb-4">OCR Uploader</h2>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100"
        />
        <button
          type="submit"
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Extract Text'}
        </button>
      </form>
      {error && <p className="mt-3 text-red-600">{error}</p>}
      {text && (
        <div className="mt-3 p-3 border rounded bg-gray-50">
          <h3 className="font-bold mb-2">Extracted text</h3>
          <pre className="whitespace-pre-wrap text-sm text-gray-900">{text}</pre>
        </div>
      )}
    </div>
  )
}
