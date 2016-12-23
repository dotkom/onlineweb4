export const csrfSafeMethod = method => (
  // these HTTP methods do not require CSRF protection
  /^(GET|HEAD|OPTIONS|TRACE)$/.test(method)
);

export default {};
