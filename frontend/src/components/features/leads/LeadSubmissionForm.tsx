"use client";

import { CheckCircle2, Loader2, MapPin, SendHorizontal, UserRound } from "lucide-react";
import { useMemo, useState } from "react";
import type { FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import { createLead } from "@/lib/api/endpoints/leads";
import type { LeadCreateDto } from "@/types/lead";

type FieldName = "name" | "email" | "company" | "role" | "propertyAddress" | "city" | "state" | "country";

type FormValues = Record<FieldName, string>;
type FormErrors = Partial<Record<FieldName, string>>;

const initialValues: FormValues = {
  name: "",
  email: "",
  company: "",
  role: "",
  propertyAddress: "",
  city: "",
  state: "",
  country: "US"
};

const fieldLabels: Record<FieldName, string> = {
  name: "Name",
  email: "Email address",
  company: "Company",
  role: "Role",
  propertyAddress: "Property address",
  city: "City",
  state: "State",
  country: "Country"
};

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function LeadSubmissionForm() {
  const [values, setValues] = useState<FormValues>(initialValues);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const trimmedValues = useMemo(() => trimValues(values), [values]);

  async function submitLead(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextErrors = validate(trimmedValues);
    setErrors(nextErrors);
    setSubmitError(null);

    if (Object.keys(nextErrors).length > 0) {
      return;
    }

    setIsSubmitting(true);
    try {
      await createLead(toLeadCreateDto(trimmedValues));
      setSubmitted(true);
      window.setTimeout(() => setToast(null), 2600);
    } catch {
      setSubmitError("Signal could not submit this lead. Check the backend connection and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function updateField(field: FieldName, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
    setErrors((current) => {
      if (!current[field]) {
        return current;
      }
      const { [field]: _cleared, ...remaining } = current;
      return remaining;
    });
  }

  return (
    <main className="request-demo-page">
      <Toast message={toast} />
      <section className="request-demo-shell">
        <div className="request-demo-brand" aria-label="Signal">
          <span className="signal-mark request-demo-mark" aria-hidden="true">
            <svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none">
              <path
                d="M4 15.5c3.2 0 3.2-7 6.4-7s3.2 7 6.4 7"
                stroke="currentColor"
                strokeLinecap="round"
                strokeWidth="2.2"
              />
              <circle cx="19.4" cy="6" fill="currentColor" r="2.1" />
            </svg>
          </span>
          <span>Signal</span>
        </div>

        <div className="request-demo-grid">
          <aside className="request-demo-copy">
            <h1>Interested? We would love to hear from you!</h1>
            <p>
              Submit a request for a demo and our team will reach out to you shortly.
            </p>
            <div className="request-demo-proof" aria-label="Submission flow">
            </div>
          </aside>

          <section className="surface-card request-demo-card" aria-label="Lead submission form">
            {submitted ? (
              <SuccessPanel />
            ) : (
              <form noValidate onSubmit={submitLead}>
                <div className="request-form-header">
                  <div>
                    <h2>Request for Demo</h2>
                  </div>
                </div>

                <fieldset className="request-form-section">
                  <legend>
                    <UserRound size={16} /> Contact info
                  </legend>
                  <div className="request-field-grid">
                    <Field
                      error={errors.name}
                      label={fieldLabels.name}
                      name="name"
                      onChange={updateField}
                      placeholder="Sample Contact"
                      value={values.name}
                    />
                    <Field
                      error={errors.email}
                      label={fieldLabels.email}
                      name="email"
                      onChange={updateField}
                      placeholder="contact@operator.example"
                      type="email"
                      value={values.email}
                    />
                    <Field
                      error={errors.company}
                      label={fieldLabels.company}
                      name="company"
                      onChange={updateField}
                      placeholder="Multifamily Operator"
                      value={values.company}
                    />
                    <Field
                      error={errors.role}
                      label={fieldLabels.role}
                      name="role"
                      onChange={updateField}
                      placeholder="VP Leasing"
                      value={values.role}
                    />
                  </div>
                </fieldset>

                <fieldset className="request-form-section">
                  <legend>
                    <MapPin size={16} /> Building
                  </legend>
                  <div className="request-field-grid">
                    <Field
                      className="request-field-wide"
                      error={errors.propertyAddress}
                      label={fieldLabels.propertyAddress}
                      name="propertyAddress"
                      onChange={updateField}
                      placeholder="100 Main St"
                      value={values.propertyAddress}
                    />
                    <Field
                      error={errors.city}
                      label={fieldLabels.city}
                      name="city"
                      onChange={updateField}
                      placeholder="Austin"
                      value={values.city}
                    />
                    <Field
                      error={errors.state}
                      label={fieldLabels.state}
                      name="state"
                      onChange={updateField}
                      placeholder="TX"
                      value={values.state}
                    />
                    <Field
                      error={errors.country}
                      label={fieldLabels.country}
                      name="country"
                      onChange={updateField}
                      placeholder="US"
                      value={values.country}
                    />
                  </div>
                </fieldset>

                {submitError && (
                  <p className="request-submit-error" role="alert">
                    {submitError}
                  </p>
                )}

                <div className="request-form-actions">
                  <Button className="request-submit-button" disabled={isSubmitting} type="submit" variant="primary">
                    {isSubmitting ? (
                      <>
                        <Loader2 className="request-spin" size={16} /> Submitting
                      </>
                    ) : (
                      <>
                        <SendHorizontal size={16} /> Submit
                      </>
                    )}
                  </Button>
                  <span className="request-form-note">All fields are required.</span>
                </div>
              </form>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}

interface FieldProps {
  className?: string;
  error?: string;
  label: string;
  name: FieldName;
  onChange: (field: FieldName, value: string) => void;
  placeholder: string;
  type?: string;
  value: string;
}

function Field({ className, error, label, name, onChange, placeholder, type = "text", value }: FieldProps) {
  const errorId = `${name}-error`;

  return (
    <label className={className ? `request-field ${className}` : "request-field"}>
      <span>{label}</span>
      <input
        aria-describedby={error ? errorId : undefined}
        aria-invalid={error ? "true" : "false"}
        autoComplete={autoCompleteFor(name)}
        name={name}
        onChange={(event) => onChange(name, event.target.value)}
        placeholder={placeholder}
        required
        type={type}
        value={value}
      />
      {error && (
        <span className="request-field-error" id={errorId} role="alert">
          {error}
        </span>
      )}
    </label>
  );
}

function SuccessPanel() {
  return (
    <div className="request-success-panel">
      <span className="request-success-icon" aria-hidden="true">
        <CheckCircle2 size={28} />
      </span>
      <h2>Submission Recieved</h2>
      <p>Thank you for your taking the time to fill out our contact form. We look forward to working with you!</p>
    </div>
  );
}

function trimValues(values: FormValues): FormValues {
  return {
    name: values.name.trim(),
    email: values.email.trim(),
    company: values.company.trim(),
    role: values.role.trim(),
    propertyAddress: values.propertyAddress.trim(),
    city: values.city.trim(),
    state: values.state.trim(),
    country: values.country.trim()
  };
}

function validate(values: FormValues): FormErrors {
  const errors: FormErrors = {};

  (Object.keys(values) as FieldName[]).forEach((field) => {
    if (!values[field]) {
      errors[field] = `${fieldLabels[field]} is required.`;
    }
  });

  if (values.email && !emailPattern.test(values.email)) {
    errors.email = "Enter a valid email address.";
  }

  return errors;
}

function toLeadCreateDto(values: FormValues): LeadCreateDto {
  return {
    contact_name: values.name,
    email: values.email,
    company: values.company,
    role: values.role,
    property_address: values.propertyAddress,
    city: values.city,
    state: values.state,
    country: values.country
  };
}

function autoCompleteFor(name: FieldName) {
  const values: Record<FieldName, string> = {
    name: "name",
    email: "email",
    company: "organization",
    role: "organization-title",
    propertyAddress: "street-address",
    city: "address-level2",
    state: "address-level1",
    country: "country-name"
  };

  return values[name];
}
