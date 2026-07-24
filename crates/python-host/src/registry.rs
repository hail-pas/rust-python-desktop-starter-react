#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PythonWorker {
    Greeter,
    Statistics,
}

impl PythonWorker {
    pub const fn name(self) -> &'static str {
        match self {
            Self::Greeter => "greeter",
            Self::Statistics => "statistics",
        }
    }
}
