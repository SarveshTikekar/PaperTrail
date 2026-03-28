import { useState } from 'react'
import axios from 'axios'

export default function OCRPanel() {
  const [file, setFile] = useState(null)
  const [formType, setFormType] = useState('pan_49a')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!file) return setError('Please select an image file')

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('form_type', formType)

      const response = await axios.post('http://127.0.0.1:8000/api/lab/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
    } catch (err) {
      setError(err?.response?.data?.error || err?.response?.data?.detail || err.message || 'OCR failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white shadow-xl rounded-xl border border-gray-100">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">PaperTrail - Form Lab</h2>
      <form onSubmit={onSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Form Template</label>
          <select 
            value={formType} 
            onChange={(e) => setFormType(e.target.value)}
            className="block w-full p-2.5 bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="pan_49a">PAN Card Form 49A (English)</option>
            <option value="voter_6">Voter ID Form 6 (Bilingual/Hindi)</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Upload Form Image</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-700 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 border border-gray-300 rounded-lg bg-gray-50"
          />
        </div>

        <button
          type="submit"
          className="w-full px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors shadow-lg disabled:bg-blue-300"
          disabled={loading}
        >
          {loading ? 'Processing OCR...' : 'Start Extraction'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-4 text-sm text-red-800 rounded-lg bg-red-50 border border-red-200">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-8 p-4 border rounded-lg bg-gray-50 shadow-inner">
          <h3 className="text-xl font-bold mb-4 text-gray-800 underline">Extraction Results (JSON)</h3>
          <div className="overflow-x-auto">
            <pre className="text-xs text-gray-900 bg-white p-4 rounded border border-gray-200 shadow-sm max-h-96 overflow-y-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
