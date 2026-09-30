from enterprise_rag_project.db.checkpointer import get_checkpointer


with get_checkpointer() as checkpointer:
    checkpointer.setup()


print("langraph checkpoint tables created")