import { useState, useEffect } from 'react'
import { getCapabilities, createCapability, updateCapability, deleteCapability, getProfiles } from '../api/client'

const EMPTY_FORM = { name: '', description: '', keywords: '', profile_id: 1 }

function KeywordChips({ keywords }) {
  const visible = keywords.slice(0, 8)
  const extra = keywords.length - visible.length
  return (
    <div className="flex flex-wrap gap-1 mt-2">
      {visible.map((kw, i) => (
        <span key={i} className="bg-blue-50 text-blue-700 text-xs px-2 py-0.5 rounded font-mono">
          {kw}
        </span>
      ))}
      {extra > 0 && (
        <span className="text-xs text-gray-400 px-1 py-0.5">+{extra} more</span>
      )}
    </div>
  )
}

function CapabilityForm({ profiles, initial, onSave, onCancel }) {
  const [form, setForm] = useState(
    initial
      ? { ...initial, keywords: (initial.keywords || []).join(', ') }
      : EMPTY_FORM
  )
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name.trim() || !form.description.trim()) {
      setError('Name and description are required.')
      return
    }
    setSaving(true)
    setError('')
    const keywords = form.keywords
      .split(',')
      .map(k => k.trim().toLowerCase())
      .filter(Boolean)
    try {
      if (initial) {
        await updateCapability(initial.id, { name: form.name, description: form.description, keywords })
      } else {
        await createCapability({ name: form.name, description: form.description, keywords, profile_id: Number(form.profile_id) })
      }
      onSave()
    } catch (err) {
      setError(err.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-blue-50 border border-blue-200 rounded-lg p-5 mb-4">
      <div className="grid grid-cols-1 gap-3 mb-3">
        <div className="flex gap-3">
          <div className="flex-1">
            <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
            <input
              type="text"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              className="w-full text-sm border border-gray-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Hyperspectral Imaging"
            />
          </div>
          {!initial && (
            <div className="w-40">
              <label className="block text-xs font-medium text-gray-600 mb-1">Profile</label>
              <select
                value={form.profile_id}
                onChange={e => setForm(f => ({ ...f, profile_id: e.target.value }))}
                className="w-full text-sm border border-gray-200 rounded px-2 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {profiles.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
          )}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Description</label>
          <textarea
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            rows={3}
            className="w-full text-sm border border-gray-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="Describe this technical capability..."
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Keywords (comma-separated)</label>
          <input
            type="text"
            value={form.keywords}
            onChange={e => setForm(f => ({ ...f, keywords: e.target.value }))}
            className="w-full text-sm border border-gray-200 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="lidar, point cloud, 3d reconstruction, ..."
          />
        </div>
      </div>

      {error && <p className="text-xs text-red-500 mb-2">{error}</p>}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={saving}
          className="px-4 py-1.5 bg-blue-700 text-white text-sm font-medium rounded hover:bg-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {saving ? 'Saving...' : (initial ? 'Save Changes' : 'Add Capability')}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-1.5 text-sm text-gray-600 border border-gray-200 rounded hover:bg-gray-100 transition-colors"
        >
          Cancel
        </button>
      </div>
    </form>
  )
}

function CapabilityCard({ cap, onEdit, onDelete }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-start justify-between gap-2 mb-1">
        <h3 className="font-semibold text-gray-900 text-sm">{cap.name}</h3>
        <div className="flex gap-2 shrink-0">
          <button
            onClick={() => onEdit(cap)}
            className="text-xs text-blue-600 hover:text-blue-800 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={() => onDelete(cap)}
            className="text-xs text-red-400 hover:text-red-600 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
      <p className="text-xs text-gray-500 leading-relaxed">{cap.description}</p>
      {cap.keywords?.length > 0 && <KeywordChips keywords={cap.keywords} />}
    </div>
  )
}

export default function Capabilities() {
  const [caps, setCaps] = useState([])
  const [profiles, setProfiles] = useState([])
  const [loading, setLoading] = useState(true)
  const [profileFilter, setProfileFilter] = useState('all')
  const [showAdd, setShowAdd] = useState(false)
  const [editing, setEditing] = useState(null)

  const load = () => {
    const profileId = profileFilter !== 'all' ? profileFilter : undefined
    return getCapabilities(profileId)
      .then(setCaps)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    getProfiles().then(setProfiles).catch(console.error)
  }, [])

  useEffect(() => {
    setLoading(true)
    load()
  }, [profileFilter])

  const handleSave = () => {
    setShowAdd(false)
    setEditing(null)
    load()
  }

  const handleDelete = async (cap) => {
    if (!confirm(`Delete capability "${cap.name}"? This cannot be undone.`)) return
    setCaps(prev => prev.filter(c => c.id !== cap.id))
    try {
      await deleteCapability(cap.id)
    } catch {
      load()
    }
  }

  const grouped = profiles.length > 0
    ? profiles.map(p => ({
        profile: p,
        items: caps.filter(c => c.profile_id === p.id),
      })).filter(g => g.items.length > 0)
    : [{ profile: null, items: caps }]

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Capabilities</h1>
          <p className="text-xs text-gray-500 mt-0.5">{caps.length} capabilities across {profiles.length} profiles</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={profileFilter}
            onChange={e => setProfileFilter(e.target.value)}
            className="text-sm border border-gray-200 rounded px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All profiles</option>
            {profiles.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          {!showAdd && !editing && (
            <button
              onClick={() => setShowAdd(true)}
              className="px-4 py-1.5 bg-blue-700 text-white text-sm font-medium rounded hover:bg-blue-800 transition-colors"
            >
              + Add Capability
            </button>
          )}
        </div>
      </div>

      {showAdd && (
        <CapabilityForm
          profiles={profiles}
          initial={null}
          onSave={handleSave}
          onCancel={() => setShowAdd(false)}
        />
      )}

      {loading ? (
        <div className="text-center text-gray-400 py-12">Loading...</div>
      ) : caps.length === 0 ? (
        <div className="text-center text-gray-400 py-12">No capabilities found.</div>
      ) : (
        grouped.map(({ profile, items }) => (
          <div key={profile?.id ?? 'all'} className="mb-8">
            {profile && (
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                {profile.name}
              </h2>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {items.map(cap => (
                editing?.id === cap.id ? (
                  <div key={cap.id} className="md:col-span-2">
                    <CapabilityForm
                      profiles={profiles}
                      initial={editing}
                      onSave={handleSave}
                      onCancel={() => setEditing(null)}
                    />
                  </div>
                ) : (
                  <CapabilityCard
                    key={cap.id}
                    cap={cap}
                    onEdit={setEditing}
                    onDelete={handleDelete}
                  />
                )
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
