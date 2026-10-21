#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <chrono>
#include <ctime>
#include <cstdlib>
#include <cstdio>
#include <sys/wait.h>

#include <grpcpp/grpcpp.h>
#include "file_processor.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerReaderWriter;
using grpc::Status;
using namespace file_processor;

class FileProcessorServiceImpl final : public FileProcessorService::Service {
private:
    // ==============================================================================
    // IMPLEMENTAÇÃO SUA (MÉTODOS AUXILIARES)
    // ==============================================================================
    void LogOperation(const std::string& type, const std::string& service,
                      const std::string& file, const std::string& msg) {
        // 1. Data e hora atuais
        std::time_t now = std::chrono::system_clock::to_time_t(
            std::chrono::system_clock::now());
        char ts[32];
        std::strftime(ts, sizeof(ts), "%Y-%m-%d %H:%M:%S", std::localtime(&now));

        // 2. Abre em modo de adição
        std::ofstream log("server.log", std::ios::app);
        if (!log) {
            std::cerr << "Nao foi possivel abrir server.log" << std::endl;
            return;
        }

        // 3. Formata e escreve a linha
        log << "[" << ts << "] [" << type << "] servico=" << service
            << " arquivo=" << (file.empty() ? "-" : file)
            << " msg=" << msg << "\n";

        // 4. Fecha (o destrutor também fecharia)
        log.close();
    }

    // Aceita apenas nomes simples, evitando injeção de comandos no std::system()
    static bool SafeName(const std::string& name) {
        if (name.empty() || name.size() > 200 || name[0] == '.') return false;
        for (char c : name) {
            bool ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
                      (c >= '0' && c <= '9') || c == '.' || c == '_' || c == '-';
            if (!ok) return false;
        }
        return true;
    }

    // ==============================================================================
    // MÉTODOS AUXILIARES FORNECIDOS (NÃO ALTERAR)
    // ==============================================================================
    bool ReceiveFile(ServerReaderWriter<FileResponse, FileRequest>* stream,
                     std::string& filepath, std::string& original_name,
                     FileRequest& last_req) {
        FileRequest req;
        std::ofstream outfile;
        bool first = true;

        while (stream->Read(&req)) {
            if (first) {
                original_name = req.file_name();
                filepath = "/tmp/input_" + original_name;
                outfile.open(filepath, std::ios::binary);
                last_req = req;
                first = false;
            }
            if (req.has_file_content()) {
                outfile.write(req.file_content().content().c_str(),
                              req.file_content().content().size());
            }
        }
        if (outfile.is_open()) outfile.close();
        return !first;
    }

    Status SendFile(ServerReaderWriter<FileResponse, FileRequest>* stream,
                    const std::string& out_filepath, const std::string& out_filename) {
        std::ifstream infile(out_filepath, std::ios::binary);
        if (!infile) return Status(grpc::StatusCode::INTERNAL, "Falha ao ler output");

        FileResponse resp;
        resp.set_success(true);
        resp.set_file_name(out_filename);
        resp.set_status_message("Sucesso");

        char buffer[1024];
        while (infile.read(buffer, sizeof(buffer)) || infile.gcount() > 0) {
            FileChunk* chunk = new FileChunk();
            chunk->set_content(buffer, infile.gcount());
            resp.set_allocated_file_content(chunk);
            stream->Write(resp);
            resp.clear_file_content();
        }
        return Status::OK;
    }

public:
    // ==============================================================================
    // IMPLEMENTAÇÃO SUA (SERVIÇOS gRPC)
    // ==============================================================================
    Status CompressPDF(ServerContext* context,
                       ServerReaderWriter<FileResponse, FileRequest>* stream) override {
        const std::string service = "CompressPDF";
        std::string in_path, original_name;
        FileRequest first_req;

        // 1. Recebe o arquivo enviado em stream
        if (!ReceiveFile(stream, in_path, original_name, first_req)) {
            LogOperation("FALHA", service, "", "Nenhum dado recebido do cliente");
            return Status(grpc::StatusCode::INVALID_ARGUMENT, "Nenhum arquivo recebido");
        }
        LogOperation("INICIO", service, original_name, "Requisicao recebida");

        // Valida o nome antes de montar o comando de shell
        if (!SafeName(original_name)) {
            std::remove(in_path.c_str());
            LogOperation("FALHA", service, original_name, "Nome de arquivo invalido");
            return Status(grpc::StatusCode::INVALID_ARGUMENT, "Nome de arquivo invalido");
        }

        std::string out_path = "/tmp/output_" + original_name;

        // 2. Comando do Ghostscript
        std::string cmd =
            "gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook "
            "-dNOPAUSE -dQUIET -dBATCH -sOutputFile='" + out_path + "' '" + in_path +
            "' > /dev/null 2>&1";

        // 3. Executa
        int ret = std::system(cmd.c_str());
        int code = (ret != -1 && WIFEXITED(ret)) ? WEXITSTATUS(ret) : -1;

        // Verifica se a saída existe e não está vazia
        std::ifstream check(out_path, std::ios::binary | std::ios::ate);
        bool out_ok = check.good() && check.tellg() > 0;
        check.close();

        Status result = Status::OK;
        if (code != 0 || !out_ok) {
            // 4a. Registra falha
            LogOperation("FALHA", service, original_name,
                         "Ghostscript falhou (codigo de retorno " + std::to_string(code) +
                         "); arquivo invalido ou corrompido");
            result = Status(grpc::StatusCode::INTERNAL,
                            "Falha ao comprimir o PDF (arquivo invalido?)");
        } else {
            // 4b. Registra sucesso e 5. devolve o arquivo comprimido
            result = SendFile(stream, out_path, original_name);
            if (result.ok()) {
                LogOperation("SUCESSO", service, original_name, "PDF comprimido e enviado");
            } else {
                LogOperation("FALHA", service, original_name, result.error_message());
            }
        }

        // 6. Remove os temporários
        std::remove(in_path.c_str());
        std::remove(out_path.c_str());
        return result;
    }

    // ==============================================================================
    // MÉTODOS IGNORADOS PARA ESTA ENTREGA
    // ==============================================================================
    Status ConvertToTXT(ServerContext* /*context*/,
                        ServerReaderWriter<FileResponse, FileRequest>* /*stream*/) override {
        // Não é necessário implementar para esta atividade.
        return Status::OK;
    }

    Status ConvertImageFormat(ServerContext* /*context*/,
                              ServerReaderWriter<FileResponse, FileRequest>* /*stream*/) override {
        // Não é necessário implementar para esta atividade.
        return Status::OK;
    }

    Status ResizeImage(ServerContext* /*context*/,
                       ServerReaderWriter<FileResponse, FileRequest>* /*stream*/) override {
        // Não é necessário implementar para esta atividade.
        return Status::OK;
    }
};

void RunServer() {
    std::string server_address("0.0.0.0:50051");
    FileProcessorServiceImpl service;

    ServerBuilder builder;
    builder.AddListeningPort(server_address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Servidor gRPC operacional em " << server_address << std::endl;
    server->Wait();
}

int main() {
    RunServer();
    return 0;
}
