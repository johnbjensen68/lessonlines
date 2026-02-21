import { useState, useEffect, useCallback } from 'react';
import { getCandidates, getCandidate, getHarvestBatches, promoteCandidate, rejectCandidate } from '../api/candidates';
import { getTopics } from '../api/events';
import { CandidateEvent, CandidateEventDetail, HarvestBatch } from '../types';
import Header from '../components/layout/Header';

type StatusFilter = 'pending' | 'approved' | 'rejected';

export default function AdminReview() {
  const [batches, setBatches] = useState<HarvestBatch[]>([]);
  const [selectedBatchId, setSelectedBatchId] = useState<string | null>(null);
  const [candidates, setCandidates] = useState<CandidateEvent[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CandidateEventDetail | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('pending');
  const [topicMap, setTopicMap] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [detailLoading, setDetailLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [rejectNotes, setRejectNotes] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);

  // Load topics and batches on mount
  useEffect(() => {
    getTopics().then((topics) => {
      const map: Record<string, string> = {};
      topics.forEach((t) => { map[t.id] = t.name; });
      setTopicMap(map);
    });
    getHarvestBatches().then((data) => {
      setBatches(data);
      if (data.length > 0) setSelectedBatchId(data[0].id);
    });
  }, []);

  const selectedBatch = batches.find((b) => b.id === selectedBatchId) ?? null;

  const fetchCandidates = useCallback(async () => {
    if (!selectedBatchId) return;
    setLoading(true);
    try {
      const data = await getCandidates({ status: statusFilter, harvest_batch_id: selectedBatchId });
      setCandidates(data);
    } catch (err) {
      console.error('Failed to fetch candidates:', err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, selectedBatchId]);

  useEffect(() => {
    fetchCandidates();
    setSelectedId(null);
    setDetail(null);
  }, [fetchCandidates]);

  useEffect(() => {
    if (!selectedId) { setDetail(null); return; }
    setDetailLoading(true);
    getCandidate(selectedId)
      .then(setDetail)
      .catch((err) => console.error('Failed to fetch candidate detail:', err))
      .finally(() => setDetailLoading(false));
  }, [selectedId]);

  const handlePromote = async () => {
    if (!selectedId) return;
    setActionLoading(true);
    try {
      await promoteCandidate(selectedId);
      await fetchCandidates();
      setSelectedId(null);
      setDetail(null);
    } catch (err) {
      console.error('Failed to promote candidate:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedId) return;
    setActionLoading(true);
    try {
      await rejectCandidate(selectedId, rejectNotes);
      setRejectNotes('');
      setShowRejectForm(false);
      await fetchCandidates();
      setSelectedId(null);
      setDetail(null);
    } catch (err) {
      console.error('Failed to reject candidate:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const tabs: { key: StatusFilter; label: string }[] = [
    { key: 'pending', label: 'Pending' },
    { key: 'approved', label: 'Approved' },
    { key: 'rejected', label: 'Rejected' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header />
      <div className="flex-1 flex overflow-hidden">

        {/* Left panel */}
        <div className="w-96 border-r border-slate-200 bg-white flex flex-col">

          {/* Batch selector */}
          <div className="p-4 border-b border-slate-200">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide block mb-2">
              Batch
            </label>
            {batches.length === 0 ? (
              <p className="text-sm text-slate-400">No batches found</p>
            ) : (
              <select
                value={selectedBatchId ?? ''}
                onChange={(e) => {
                  setSelectedBatchId(e.target.value);
                  setSelectedId(null);
                  setDetail(null);
                }}
                className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {batches.map((batch) => (
                  <option key={batch.id} value={batch.id}>
                    {topicMap[batch.topic_id] ?? 'Unknown Topic'} — {batch.source_name}
                  </option>
                ))}
              </select>
            )}

            {/* Selected batch topic callout */}
            {selectedBatch && topicMap[selectedBatch.topic_id] && (
              <div className="mt-3 px-3 py-2 bg-primary-50 rounded-md flex items-center gap-2">
                <span className="text-xs font-semibold text-primary-700 uppercase tracking-wide">Topic</span>
                <span className="text-sm font-medium text-primary-900">{topicMap[selectedBatch.topic_id]}</span>
                <span className={`ml-auto text-xs px-1.5 py-0.5 rounded font-medium ${
                  selectedBatch.status === 'completed' ? 'bg-green-100 text-green-700' :
                  selectedBatch.status === 'running' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {selectedBatch.status}
                </span>
              </div>
            )}
          </div>

          {/* Status filter tabs */}
          <div className="px-4 py-3 border-b border-slate-200">
            <div className="flex gap-1">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setStatusFilter(tab.key)}
                  className={`px-3 py-1.5 text-sm rounded-md font-medium transition-colors ${
                    statusFilter === tab.key
                      ? 'bg-primary-500 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Candidate list */}
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
              </div>
            ) : candidates.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                No {statusFilter} candidates
              </div>
            ) : (
              candidates.map((candidate) => (
                <button
                  key={candidate.id}
                  onClick={() => setSelectedId(candidate.id)}
                  className={`w-full text-left p-4 border-b border-slate-100 hover:bg-slate-50 transition-colors ${
                    selectedId === candidate.id ? 'bg-primary-50 border-l-4 border-l-primary-500' : ''
                  }`}
                >
                  <div className="flex gap-3">
                    {candidate.image_url && (
                      <img
                        src={candidate.image_url}
                        alt=""
                        className="w-12 h-12 rounded object-cover flex-shrink-0"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${
                          candidate.existing_event_id
                            ? 'bg-amber-100 text-amber-700'
                            : 'bg-green-100 text-green-700'
                        }`}>
                          {candidate.existing_event_id ? 'Update' : 'New'}
                        </span>
                        {candidate.confidence_score !== null && (
                          <span className="text-xs text-slate-400">
                            {Math.round(candidate.confidence_score * 100)}%
                          </span>
                        )}
                      </div>
                      <h3 className="font-medium text-slate-800 text-sm truncate">{candidate.title}</h3>
                      <p className="text-xs text-slate-500 mt-0.5">{candidate.date_display}</p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Right panel - Detail view */}
        <div className="flex-1 overflow-y-auto">
          {detailLoading ? (
            <div className="flex items-center justify-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            </div>
          ) : !detail ? (
            <div className="flex items-center justify-center h-full text-slate-400">
              Select a candidate to review
            </div>
          ) : (
            <div className="p-6 max-w-4xl">
              {/* Header badges */}
              <div className="flex items-center gap-3 mb-6">
                <span className={`text-sm px-2 py-1 rounded font-medium ${
                  detail.existing_event_id
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-green-100 text-green-700'
                }`}>
                  {detail.existing_event_id ? 'Proposed Update' : 'New Event'}
                </span>
                <span className={`text-sm px-2 py-1 rounded font-medium ${
                  detail.status === 'pending' ? 'bg-blue-100 text-blue-700' :
                  detail.status === 'approved' ? 'bg-green-100 text-green-700' :
                  'bg-red-100 text-red-700'
                }`}>
                  {detail.status}
                </span>
              </div>

              {detail.existing_event ? (
                <ComparisonView candidate={detail} existing={detail.existing_event} />
              ) : (
                <CandidateFields candidate={detail} />
              )}

              {/* Action buttons */}
              {detail.status === 'pending' && (
                <div className="mt-8 pt-6 border-t border-slate-200">
                  {showRejectForm ? (
                    <div className="space-y-3">
                      <textarea
                        value={rejectNotes}
                        onChange={(e) => setRejectNotes(e.target.value)}
                        placeholder="Rejection notes (optional)..."
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm resize-none h-24 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={handleReject}
                          disabled={actionLoading}
                          className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 disabled:opacity-50"
                        >
                          {actionLoading ? 'Rejecting...' : 'Confirm Reject'}
                        </button>
                        <button
                          onClick={() => { setShowRejectForm(false); setRejectNotes(''); }}
                          className="px-4 py-2 bg-slate-100 text-slate-600 rounded-lg text-sm font-medium hover:bg-slate-200"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-3">
                      <button
                        onClick={handlePromote}
                        disabled={actionLoading}
                        className="px-6 py-2.5 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
                      >
                        {actionLoading ? 'Promoting...' : 'Approve & Promote'}
                      </button>
                      <button
                        onClick={() => setShowRejectForm(true)}
                        disabled={actionLoading}
                        className="px-6 py-2.5 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 disabled:opacity-50"
                      >
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              )}

              {detail.status !== 'pending' && detail.reviewed_at && (
                <div className="mt-6 p-4 bg-slate-50 rounded-lg text-sm text-slate-600">
                  <p>Reviewed: {new Date(detail.reviewed_at).toLocaleString()}</p>
                  {detail.review_notes && <p className="mt-1">Notes: {detail.review_notes}</p>}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function CandidateFields({ candidate }: { candidate: CandidateEventDetail }) {
  return (
    <div className="space-y-6">
      {candidate.image_url && (
        <img src={candidate.image_url} alt={candidate.title} className="w-full max-w-md rounded-lg" />
      )}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">{candidate.title}</h1>
        <p className="text-slate-500 mt-1">{candidate.date_display}</p>
      </div>
      <FieldRow label="Description" value={candidate.description} />
      <FieldRow label="Location" value={candidate.location} />
      <FieldRow label="Significance" value={candidate.significance} />
      <FieldRow label="Source" value={candidate.source_citation || candidate.source_url} />
      <FieldRow label="Source Name" value={candidate.source_name} />
      <FieldRow label="Date Precision" value={candidate.date_precision} />
      {candidate.tags.length > 0 && (
        <div>
          <span className="text-sm font-medium text-slate-600">Tags:</span>
          <div className="flex gap-1 mt-1">
            {candidate.tags.map((tag) => (
              <span key={tag.id} className="px-2 py-0.5 bg-slate-100 rounded text-xs text-slate-600">{tag.name}</span>
            ))}
          </div>
        </div>
      )}
      {candidate.standards.length > 0 && (
        <div>
          <span className="text-sm font-medium text-slate-600">Standards:</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {candidate.standards.map((s) => (
              <span key={s.id} className="px-2 py-0.5 bg-blue-50 rounded text-xs text-blue-600">{s.code}: {s.title}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function FieldRow({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div>
      <span className="text-sm font-medium text-slate-600">{label}</span>
      <p className="text-slate-800 mt-0.5">{value}</p>
    </div>
  );
}

interface ComparisonViewProps {
  candidate: CandidateEventDetail;
  existing: NonNullable<CandidateEventDetail['existing_event']>;
}

function ComparisonView({ candidate, existing }: ComparisonViewProps) {
  const fields: { label: string; candidateVal: string | null | undefined; existingVal: string | null | undefined }[] = [
    { label: 'Title', candidateVal: candidate.title, existingVal: existing.title },
    { label: 'Description', candidateVal: candidate.description, existingVal: existing.description },
    { label: 'Date', candidateVal: candidate.date_display, existingVal: existing.date_display },
    { label: 'Location', candidateVal: candidate.location, existingVal: existing.location },
    { label: 'Significance', candidateVal: candidate.significance, existingVal: existing.significance },
    { label: 'Source URL', candidateVal: candidate.source_url, existingVal: existing.source_url },
    { label: 'Source Citation', candidateVal: candidate.source_citation, existingVal: existing.source_citation },
    { label: 'Image URL', candidateVal: candidate.image_url, existingVal: existing.image_url },
  ];

  return (
    <div className="space-y-4">
      {candidate.image_url && (
        <img src={candidate.image_url} alt={candidate.title} className="w-full max-w-md rounded-lg" />
      )}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="font-semibold text-slate-500 pb-2 border-b">Existing Event</div>
        <div className="font-semibold text-slate-500 pb-2 border-b">Proposed Change</div>
      </div>
      {fields.map((field) => {
        const changed = field.candidateVal !== field.existingVal;
        return (
          <div key={field.label}>
            <span className="text-sm font-medium text-slate-600">{field.label}</span>
            <div className="grid grid-cols-2 gap-4 mt-1">
              <div className={`p-2 rounded text-sm ${changed ? 'bg-red-50 text-red-800' : 'text-slate-700'}`}>
                {field.existingVal || <span className="text-slate-300 italic">empty</span>}
              </div>
              <div className={`p-2 rounded text-sm ${changed ? 'bg-green-50 text-green-800' : 'text-slate-700'}`}>
                {field.candidateVal || <span className="text-slate-300 italic">empty</span>}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
