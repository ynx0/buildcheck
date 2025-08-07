-- Employee Submitter Trigger
-- This always checks that the case is being submitted by employee only.
create or replace function check_submitter_role()
returns trigger as $$
begin
  if not exists (
    select 1 from users where id = new.submitter_id and role = 'employee'
  ) then
    raise exception 'Submitter for case was not an employee. Only an employee can be a submitter.';
  end if;
  return new;
end;
$$ language plpgsql;


create or replace trigger enforce_submitter_role
before insert or update on cases
for each row execute function check_submitter_role();
