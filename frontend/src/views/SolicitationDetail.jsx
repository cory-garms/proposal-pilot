import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSolicitation, getAlignment, createProject, triggerAlignment } from '../api/client'

const scoreColor = (score) => {
  if (score >= 0.7) return 'border-green-400 bg-green-50'
  if (score >= 0.4) return 'border-yellow-400 bg-yellow-50'
  return 'border-gray-200 bg-gray-50'
}

const scoreTextColor = (score) => {
  if (score >= 0.7) return 'text-green-700'
  if (score >= 0.4) return 'text-yellow-700'
  return 'text-gray-500'
}

const scoreBadgeBg = (score) => {
  if (score >= 0.7) return 'bg-green-500'
  if (score >= 0.4) return 'bg-yellow-400'
  return 'bg-gray-300'
}

export default function SolicitationDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [sol, setSol] = useState(null)
  const [alignment, setAlignment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [realigning, setRealigning] = useState(false)
  const [error, setError] = useState('')

  const fetchAlignment = useCallback(async () => {
    try {
      const profileId = localStorage.getItem('profileId') || '1'
      const a = await getAlignment(id, profileId)
      setAlignment(a)
    } catch (e) {
      console.error(e)
    }
  }, [id])

  useEffect(() => {
    getSolicitation(id)
      .then(setSol)
      .catch(() => setError('Failed to load solicitation'))
      .finally(() => setLoading(false))
    fetchAlignment()
  }, [id, fetchAlignment])

  const handleRealign = async () => {
    setRealigning(true)
    setError('')
    try {
      await triggerAlignment(id)
      await fetchAlignment()
    } catch (e) {
      setError('Alignment failed: ' + (e.message || 'unknown'))
    } finally {
      setRealigning(false)
    }
  }

  const handleCreateProject = async () => {
    setCreating(true)
    try {
      const project = await createProject({
        solicitation_id: parseInt(id),
        title: `Phase I - ${sol.title}`,
      })
      navigate(`/projects/${project.id}`)
    } catch (e) {
      setError('Failed to create project: ' + (e.message || 'unknown'))
      setCreating(false)
    }
  }

  if (loading) return <div className="p-8 text-center text-gray-400">Loading...</div>
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>
  if (!sol) return null

  const topScore = alignment?.scores?.[0]

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <button
        onClick={() => navigate('/')}
        className="text-sm text-blue-600 hover:underline mb-4 inline-block"
      >
        &larr; Back to solicitations
      </button>

      <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                {sol.agency}
              </span>
              {sol.topic_number && (
                <span className="text-xs font-mono text-gray-500">{sol.topic_number}</span>
              )}
            </div>
            <h1 className="text-xl font-bold text-gray-900 mb-1">{sol.title}</h1>
            {sol.open_date && (
              <p className="text-sm text-gray-500 mb-1">Open Date: {sol.open_date}</p>
            )}
            {sol.close_date && (
              <p className="text-sm text-gray-500 font-medium">Close Date: <span className="text-gray-900">{sol.close_date}</span></p>
            )}
            {!sol.close_date && sol.deadline && (
              <p className="text-sm text-gray-500 font-medium">Deadline: <span className="text-gray-900">{sol.deadline}</span></p>
            )}
          </div>
          <button
            onClick={handleCreateProject}
            disabled={creating}
            className="shrink-0 px-4 py-2 bg-blue-700 text-white text-sm font-medium rounded hover:bg-blue-800 disabled:opacity-50 transition-colors"
          >
            {creating ? 'Creating...' : 'Create Project'}
          </button>
        </div>
      </div>

      {/* Alignment Score Cards */}
      {(alignment?.scores?.length > 0 || realigning) && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">
              Capability Alignment
            </h2>
            <button
              onClick={handleRealign}
              disabled={realigning}
              className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              {realigning ? 'Scoring...' : '🔄 Re-run Alignment'}
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {alignment.scores.map((s) => (
              <div
                key={s.capability_id}
                className={`border rounded-lg p-4 ${scoreColor(s.score)}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-gray-800">{s.capability}</span>
                  <div className="flex items-center gap-1.5">
                    <div className={`w-2 h-2 rounded-full ${scoreBadgeBg(s.score)}`} />
                    <span className={`text-sm font-mono font-bold ${scoreTextColor(s.score)}`}>
                      {s.score.toFixed(2)}
                    </span>
                  </div>
                </div>
                {/* Score bar */}
                <div className="h-1.5 bg-white rounded-full overflow-hidden mb-2">
                  <div
                    className={`h-full rounded-full transition-all ${
                      s.score >= 0.7 ? 'bg-green-500' : s.score >= 0.4 ? 'bg-yellow-400' : 'bg-gray-300'
                    }`}
                    style={{ width: `${Math.round(s.score * 100)}%` }}
                  />
                </div>
                <p className="text-xs text-gray-600 leading-relaxed">{s.rationale}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full Description */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
        <h2 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
          Description
        </h2>
        {sol.url && (
          <a
            href={sol.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-blue-600 hover:underline mb-3 block"
          >
            View official solicitation &rarr;
          </a>
        )}
        <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
          {sol.description || 'No description available.'}
        </div>
      </div>
    </div>
  )
}
