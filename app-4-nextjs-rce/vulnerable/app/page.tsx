import { addTask, getTasks } from "./actions";

export default async function Home() {
  const tasks = await getTasks();

  return (
    <div>
      <h1>Task Manager</h1>
      <p style={{ color: "#666", marginBottom: "2rem" }}>Add and manage your tasks</p>

      <form action={addTask} style={{ marginBottom: "2rem" }}>
        <div style={{ marginBottom: "1rem" }}>
          <input
            type="text"
            name="title"
            placeholder="Task title"
            required
            style={{
              width: "100%",
              padding: "0.5rem",
              fontSize: "1rem",
              border: "1px solid #ddd",
              borderRadius: "4px",
            }}
          />
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <textarea
            name="description"
            placeholder="Task description"
            rows={3}
            style={{
              width: "100%",
              padding: "0.5rem",
              fontSize: "1rem",
              border: "1px solid #ddd",
              borderRadius: "4px",
            }}
          />
        </div>
        <button
          type="submit"
          style={{
            padding: "0.5rem 1rem",
            fontSize: "1rem",
            backgroundColor: "#0070f3",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Add Task
        </button>
      </form>

      <h2>Tasks</h2>
      {tasks.length === 0 ? (
        <p style={{ color: "#999" }}>No tasks yet. Add one above!</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {tasks.map((task, index) => (
            <li
              key={index}
              style={{
                border: "1px solid #ddd",
                borderRadius: "4px",
                padding: "1rem",
                marginBottom: "1rem",
              }}
            >
              <h3 style={{ margin: "0 0 0.5rem 0" }}>{task.title}</h3>
              {task.description && <p style={{ margin: 0, color: "#666" }}>{task.description}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
