"use client";

interface Props {
  subject: string;
  body: string;
  onSubjectChange: (value: string) => void;
  onBodyChange: (value: string) => void;
}

export function EditableDraft({ subject, body, onSubjectChange, onBodyChange }: Props) {
  return (
    <div className="editable-draft">
      <label>
        <span className="eyebrow">Subject</span>
        <input value={subject} onChange={(event) => onSubjectChange(event.target.value)} />
      </label>
      <label>
        <span className="eyebrow">Body</span>
        <textarea value={body} onChange={(event) => onBodyChange(event.target.value)} rows={12} />
      </label>
    </div>
  );
}
