# Task 1 - viva questions and answers

**Task 1 - Problem Definition and Scope**

Source: section G of [task-01-problem-definition-and-scope.md](../../task-01-problem-definition-and-scope.md) - answers checked against the
repository and the evidence in this project.

1. **What problem does your project solve?**
   Two problems: hotel guests cannot book rooms themselves and double bookings
   happen; and the software is released manually without tests. The portal
   solves the first, the CI/CD pipeline the second.
2. **Who are your stakeholders?**
   Hotel owner, front-desk staff, guests, the development team, operations
   (who deploy and roll back), and the course instructor.
3. **What is an MVP and what is yours?**
   The smallest useful version. Ours is six workflows: register/login,
   availability, booking request, confirmation, cancellation, status tracking.
4. **Why did you leave payments out?**
   Payments add security and legal requirements (card data) that do not help
   demonstrate DevOps; they are listed as future work.
5. **What makes your success criteria "measurable"?**
   Each has a number or yes/no check: 90 tests passing, pipeline under 5
   minutes (build #11 took 103 s), `changed=0` on a repeat Ansible run.
6. **Did you interview real hotel staff?**
   No. The stakeholders and pain points are a reasoned model of a small
   hotel; that is a limitation, and real interviews would be the next step.
7. **Which constraint affected the design most?**
   SQLite: one writer at a time, so double-booking prevention uses a locking
   transaction and a database trigger; and the lack of a public server, which
   is why Jenkins polls Git instead of using a webhook.
8. **(Project-specific) Where is the scope written down and how is it versioned?**
   In `docs/01-problem-definition.md`, committed in Git and published on
   GitHub, so changes to scope are tracked like code changes.
9. **(Project-specific) How do you know objective O2 (no overlapping bookings) is met?**
   Tests prove it: `test_simultaneous_requests_create_only_one_booking` (10
   threads, exactly 1 booking) and `test_trigger_rejects_overlapping_insert`.
10. **Why is the delivery pipeline part of the problem definition?**
    Because a broken release would break bookings for real guests; the
    hotel's need includes "change the system safely", not just "have a website".

## Extra questions that match this demonstration

1. **Why did you not interview real hotel staff?**
   The project is a course exercise with a 10-day schedule. The users and pain points are a reasoned model of a small hotel, and the document says so. Real interviews would be the first step if this became a real product.
