// Windows GUI launcher for the offline, portable Study Coach package.
// GPL/FSF GCC and PSF Python runtime are redistributed with their own licenses.
#define UNICODE
#define _UNICODE
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <shellapi.h>
#include <string>

#pragma comment(lib, "ws2_32")
#pragma comment(lib, "shell32")

static PROCESS_INFORMATION child = {};
static HWND window_handle = nullptr;
static HWND status_label = nullptr;
static int active_port = 8780;
static std::wstring root_path;

static std::wstring location(const wchar_t* subpath) {
    return root_path + L"\\" + subpath;
}
static bool file_exists(const std::wstring& p) {
    DWORD attrs = GetFileAttributesW(p.c_str());
    return attrs != INVALID_FILE_ATTRIBUTES && !(attrs & FILE_ATTRIBUTE_DIRECTORY);
}
static void alert(const std::wstring& s) {
    MessageBoxW(window_handle, s.c_str(), L"Study Coach", MB_ICONERROR | MB_OK);
}
static bool port_free(int port) {
    SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) return false;
    sockaddr_in addr = {};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<u_short>(port));
    bool ok = bind(s, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0;
    closesocket(s);
    return ok;
}
static bool health_ok(int port) {
    SOCKET s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) return false;
    DWORD ms = 550;
    setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<const char*>(&ms), sizeof(ms));
    sockaddr_in addr = {};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(static_cast<u_short>(port));
    bool ok = false;
    if (connect(s, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0) {
        const char req[] = "GET /api/health HTTP/1.0\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n";
        send(s, req, sizeof(req)-1, 0);
        char buf[1024] = {};
        int n = recv(s,buf,sizeof(buf)-1,0);
        if (n > 0) {
            const std::string data(buf,n);
            ok = data.find("200 OK") != std::string::npos || data.find("200 ") != std::string::npos;
        }
    }
    closesocket(s);
    return ok;
}
static void open_browser() {
    const std::wstring url = L"http://127.0.0.1:" + std::to_wstring(active_port);
    ShellExecuteW(nullptr,L"open",url.c_str(),nullptr,nullptr,SW_SHOWNORMAL);
}
static bool start_backend() {
    const std::wstring python = location(L"runtime\\python.exe");
    const std::wstring server = location(L"server.py");
    const std::wstring compiler = location(L"toolchain\\bin\\g++.exe");
    if (!file_exists(python) || !file_exists(server) || !file_exists(compiler)) {
        alert(L"Missing bundled Python or C++ compiler.\nExtract the complete ZIP before opening StudyCoach.exe.");
        return false;
    }
    bool chosen = false;
    for (int p=8780; p<=8799; ++p) {
        if (port_free(p)) { active_port=p;chosen=true;break; }
    }
    if (!chosen) { alert(L"No available local port between 8780 and 8799."); return false; }

    const std::wstring compiler_dir = location(L"toolchain\\bin");
    DWORD size = GetEnvironmentVariableW(L"PATH",nullptr,0);
    std::wstring old_path(size ? size : 1, L'\0');
    if (size) { GetEnvironmentVariableW(L"PATH",&old_path[0],size); old_path.resize(wcslen(old_path.c_str())); }
    SetEnvironmentVariableW(L"PATH",(compiler_dir+L";"+old_path).c_str());
    SetEnvironmentVariableW(L"STUDY_COACH_GPP",compiler.c_str());
    SetEnvironmentVariableW(L"STUDY_COACH_PORT",std::to_wstring(active_port).c_str());
    SetEnvironmentVariableW(L"STUDY_COACH_HOST",L"127.0.0.1");
    if (file_exists(location(L"installed.flag"))) {
        wchar_t buf[32768] = {};
        DWORD n = GetEnvironmentVariableW(L"LOCALAPPDATA",buf,32768);
        if (n && n<32768) {
            std::wstring dir = std::wstring(buf) + L"\\StudyCoach\\data";
            CreateDirectoryW((std::wstring(buf)+L"\\StudyCoach").c_str(),nullptr);
            CreateDirectoryW(dir.c_str(),nullptr);
            SetEnvironmentVariableW(L"STUDY_COACH_DATA_DIR",dir.c_str());
        }
    }
    STARTUPINFOW si = {};
    si.cb = sizeof(si);
    std::wstring command = L"\"" + python + L"\" \"" + server + L"\"";
    if (!CreateProcessW(python.c_str(),&command[0],nullptr,nullptr,FALSE,
                        CREATE_NO_WINDOW,nullptr,root_path.c_str(),&si,&child)) {
        alert(L"Could not start the bundled Python runtime.");
        return false;
    }
    for (int attempt=0;attempt<65;++attempt) {
        if (health_ok(active_port)) return true;
        if (WaitForSingleObject(child.hProcess,0)==WAIT_OBJECT_0)break;
        Sleep(200);
    }
    alert(L"Study Coach server did not become healthy. Verify your antivirus did not block the executable.");
    return false;
}
static void stop_backend() {
    if (child.hProcess) {
        if (WaitForSingleObject(child.hProcess,0)!=WAIT_OBJECT_0) {
            TerminateProcess(child.hProcess,0);
            WaitForSingleObject(child.hProcess,1500);
        }
        CloseHandle(child.hProcess);
        CloseHandle(child.hThread);
        child = {};
        DeleteFileW(location(L"data\\server.pid").c_str());
    }
}
static LRESULT CALLBACK window_proc(HWND hwnd,UINT msg,WPARAM w,LPARAM l) {
    switch(msg) {
        case WM_COMMAND:
            if (LOWORD(w)==1001)open_browser();
            if (LOWORD(w)==1002)DestroyWindow(hwnd);
            return 0;
        case WM_CLOSE:DestroyWindow(hwnd);return 0;
        case WM_DESTROY:PostQuitMessage(0);return 0;
        default:return DefWindowProcW(hwnd,msg,w,l);
    }
}
int WINAPI wWinMain(HINSTANCE hInst,HINSTANCE,LPWSTR,int) {
    wchar_t module[MAX_PATH]={};
    if (!GetModuleFileNameW(nullptr,module,MAX_PATH))return 2;
    root_path=module;
    auto pos=root_path.find_last_of(L"\\/");
    if(pos==std::wstring::npos)return 3;
    root_path.resize(pos);
    WSADATA wsa={};
    if(WSAStartup(MAKEWORD(2,2),&wsa)!=0)return 4;
    WNDCLASSW wc={};
    wc.lpfnWndProc=window_proc;
    wc.hInstance=hInst;
    wc.lpszClassName=L"StudyCoachPortableLauncher";
    wc.hCursor=LoadCursorW(nullptr,IDC_ARROW);
    wc.hbrBackground=(HBRUSH)(COLOR_WINDOW+1);
    if(!RegisterClassW(&wc))return 5;
    window_handle=CreateWindowExW(0,wc.lpszClassName,L"Study Coach — C++",
        WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX,CW_USEDEFAULT,CW_USEDEFAULT,405,185,
        nullptr,nullptr,hInst,nullptr);
    if(!window_handle)return 6;
    HFONT font=(HFONT)GetStockObject(DEFAULT_GUI_FONT);
    status_label=CreateWindowW(L"STATIC",L"Starting Study Coach...",WS_VISIBLE|WS_CHILD,
        18,18,365,55,window_handle,nullptr,hInst,nullptr);
    SendMessageW(status_label,WM_SETFONT,(WPARAM)font,TRUE);
    HWND open_button=CreateWindowW(L"BUTTON",L"Open Browser",WS_VISIBLE|WS_CHILD|BS_PUSHBUTTON,
        25,94,160,32,window_handle,(HMENU)1001,hInst,nullptr);
    HWND exit_button=CreateWindowW(L"BUTTON",L"Stop Study Coach",WS_VISIBLE|WS_CHILD|BS_PUSHBUTTON,
        200,94,160,32,window_handle,(HMENU)1002,hInst,nullptr);
    SendMessageW(open_button,WM_SETFONT,(WPARAM)font,TRUE);
    SendMessageW(exit_button,WM_SETFONT,(WPARAM)font,TRUE);
    ShowWindow(window_handle,SW_SHOW);
    UpdateWindow(window_handle);
    if(start_backend()) {
        std::wstring label = L"Study Coach is running locally.\nhttp://127.0.0.1:" + std::to_wstring(active_port);
        SetWindowTextW(status_label,label.c_str());
        open_browser();
    } else {
        stop_backend();
        DestroyWindow(window_handle);
        WSACleanup();
        return 1;
    }
    MSG msg={};
    while(GetMessageW(&msg,nullptr,0,0)>0){TranslateMessage(&msg);DispatchMessageW(&msg);}
    stop_backend();
    WSACleanup();
    return 0;
}
